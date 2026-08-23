"""TLS helpers for tenant sites under *.flexloopers.com.

Modes (common_site_config.json → saas_ssl.mode):
  - per_site (default): certbot HTTP-01 per hostname during provision
  - wildcard: use shared *.domain cert from common_site_config.wildcard

Bench wildcard format (preferred once issued):
  "wildcard": {
    "domain": "*.flexloopers.com",
    "ssl_certificate": "/etc/letsencrypt/live/flexloopers-wildcard/fullchain.pem",
    "ssl_certificate_key": "/etc/letsencrypt/live/flexloopers-wildcard/privkey.pem"
  }
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import frappe
from frappe.utils import get_bench_path

from saas_master.provisioning.runner import run_command

BASE_DOMAIN = "flexloopers.com"
CERT_ROOT = Path("/etc/letsencrypt/live")
ISSUE_BIN = "/usr/local/bin/saas-ssl-issue"


def _sites_path() -> Path:
	"""Bench sites/ directory (frappe.utils has no get_sites_path on v15)."""
	return Path(get_bench_path()) / "sites"


def _file_exists(path: str | Path) -> bool:
	"""True if path is a regular file. Handles root-only /etc/letsencrypt/live (mode 700)."""
	p = Path(path)
	try:
		return p.is_file()
	except PermissionError:
		proc = subprocess.run(
			["sudo", "-n", "test", "-f", str(p)],
			capture_output=True,
			text=True,
		)
		return proc.returncode == 0


def _common_conf() -> dict:
	path = _sites_path() / "common_site_config.json"
	try:
		return json.loads(path.read_text())
	except Exception:
		return {}


def _site_config_path(site: str) -> Path:
	return _sites_path() / site / "site_config.json"


def _read_site_config(site: str) -> dict:
	path = _site_config_path(site)
	if not path.exists():
		return {}
	return json.loads(path.read_text())


def _write_site_config(site: str, cfg: dict) -> None:
	path = _site_config_path(site)
	path.write_text(json.dumps(cfg, indent=1) + "\n")


def wildcard_configured() -> bool:
	wc = _common_conf().get("wildcard") or {}
	cert = wc.get("ssl_certificate") or ""
	key = wc.get("ssl_certificate_key") or ""
	domain = wc.get("domain") or ""
	return bool(cert and key and domain and _file_exists(cert) and _file_exists(key))


def _site_matches_wildcard(site: str) -> bool:
	wc = _common_conf().get("wildcard") or {}
	domain = wc.get("domain") or ""
	if not domain:
		return False
	# "*.flexloopers.com" → match ends with ".flexloopers.com"
	if domain.startswith("*"):
		suffix = domain[1:]  # ".flexloopers.com"
		return site.endswith(suffix)
	return site.endswith("." + domain) or site == domain


def _set_site_ssl_paths(site: str, cert: str, key: str) -> None:
	cfg = _read_site_config(site)
	cfg["ssl_certificate"] = cert
	cfg["ssl_certificate_key"] = key
	_write_site_config(site, cfg)


def _issue_per_site_cert(site: str, tenant_name: str) -> tuple[str, str]:
	"""Run root helper to issue cert; return (cert, key) paths."""
	live = CERT_ROOT / site
	cert = str(live / "fullchain.pem")
	key = str(live / "privkey.pem")
	if _file_exists(cert) and _file_exists(key):
		return cert, key

	# Prefer passwordless sudo helper; fall back to direct certbot if root.
	cmd = f"sudo -n {ISSUE_BIN} {site}"
	ok, out = run_command(cmd, tenant_name, f"6/6 ssl issue {site}", timeout=300)
	if not ok:
		# Direct certbot (when worker somehow has rights) — still log
		cmd2 = (
			f"sudo -n /usr/bin/certbot certonly --nginx -d {site} --non-interactive "
			f"--agree-tos --register-unsafely-without-email "
			f"--keep-until-expiring --cert-name {site}"
		)
		ok2, out2 = run_command(cmd2, tenant_name, f"6/6 ssl issue {site}", timeout=300)
		if not ok2:
			raise RuntimeError(f"certbot failed for {site}: {(out or out2 or '')[-500:]}")

	if not (_file_exists(cert) and _file_exists(key)):
		raise RuntimeError(f"certificate files missing for {site}")
	return cert, key


def reload_nginx(tenant_name: str) -> None:
	"""Regenerate nginx.conf and reload the running nginx process.

	Important: run_command uses Popen(shlex.split(...)) — no shell — so never
	pass ``cmd1 && cmd2`` as a single string (reload would silently never run).
	"""
	ok_setup, out_setup = run_command(
		"bench setup nginx --yes", tenant_name, "6/6 nginx setup", timeout=120
	)
	if not ok_setup:
		raise RuntimeError(f"bench setup nginx failed: {(out_setup or '')[-400:]}")

	ok_test, out_test = run_command(
		"sudo -n nginx -t", tenant_name, "6/6 nginx test", timeout=60
	)
	if not ok_test:
		raise RuntimeError(f"nginx -t failed: {(out_test or '')[-400:]}")

	ok_reload, out_reload = run_command(
		"sudo -n systemctl reload nginx", tenant_name, "6/6 nginx reload", timeout=60
	)
	if not ok_reload:
		raise RuntimeError(f"nginx reload failed: {(out_reload or '')[-400:]}")


def verify_tenant_https(
	site: str,
	*,
	attempts: int = 10,
	delay: float = 2.0,
	timeout: float = 12.0,
) -> None:
	"""Confirm browsers will accept HTTPS for this hostname.

	Checks TLS handshake (chain + hostname) and a successful HTTPS response.
	Raises RuntimeError if not ready after retries (nginx reload lag, bad cert, etc.).
	"""
	import socket
	import ssl
	import time
	import urllib.request

	last_err = "unknown"
	ctx = ssl.create_default_context()

	for _ in range(attempts):
		try:
			with socket.create_connection((site, 443), timeout=timeout) as sock:
				with ctx.wrap_socket(sock, server_hostname=site) as ssock:
					# Hostname + chain already validated by wrap_socket
					_ = ssock.getpeercert()

			req = urllib.request.Request(
				f"https://{site}/",
				headers={"User-Agent": "saas-master-ssl-verify/1.0"},
				method="GET",
			)
			with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
				code = getattr(resp, "status", None) or resp.getcode()
				# Drain a tiny bit so proxies don't hang; ignore body
				try:
					resp.read(256)
				except Exception:
					pass
			if int(code) >= 200 and int(code) < 500:
				return
			last_err = f"unexpected HTTP {code}"
		except Exception as e:
			last_err = str(e)
		time.sleep(delay)

	raise RuntimeError(f"HTTPS not ready for {site}: {last_err[-400:]}")


def ensure_tenant_ssl(site: str, tenant_name: str | None = None) -> str:
	"""Best-effort HTTPS for a tenant. Returns mode used: wildcard|per_site|existing.

	Configures cert paths + nginx, then verifies live TLS. Raises only so the
	caller can treat HTTPS as pending — provisioning should still mark Active.
	"""
	tenant_name = tenant_name or site
	cfg = _read_site_config(site)
	mode_used = "per_site"

	# Already has valid paths
	if (
		cfg.get("ssl_certificate")
		and cfg.get("ssl_certificate_key")
		and _file_exists(cfg["ssl_certificate"])
		and _file_exists(cfg["ssl_certificate_key"])
	):
		reload_nginx(tenant_name)
		mode_used = "existing"
	else:
		saas_ssl = (
			(_common_conf().get("saas_ssl") or {})
			if isinstance(_common_conf().get("saas_ssl"), dict)
			else {}
		)
		mode = (saas_ssl.get("mode") or "per_site").lower()

		if mode == "wildcard" or wildcard_configured():
			if wildcard_configured() and _site_matches_wildcard(site):
				# Bench picks up common_site_config.wildcard on setup nginx
				reload_nginx(tenant_name)
				mode_used = "wildcard"
			else:
				cert, key = _issue_per_site_cert(site, tenant_name)
				_set_site_ssl_paths(site, cert, key)
				reload_nginx(tenant_name)
				mode_used = "per_site"
		else:
			cert, key = _issue_per_site_cert(site, tenant_name)
			_set_site_ssl_paths(site, cert, key)
			reload_nginx(tenant_name)
			mode_used = "per_site"

	# Prefer confirming HTTPS, but caller must not fail site creation on this.
	verify_tenant_https(site)
	return mode_used


def try_issue_wildcard(base_domain: str = BASE_DOMAIN) -> bool:
	"""Issue *.base + apex via Hostinger DNS plugin when token is configured.

	Requires common_site_config:
	  saas_ssl.hostinger_api_token
	  or env HOSTINGER_API_TOKEN
	"""
	conf = _common_conf()
	saas_ssl = conf.get("saas_ssl") or {}
	token = (
		os.environ.get("HOSTINGER_API_TOKEN")
		or saas_ssl.get("hostinger_api_token")
		or ""
	)
	if not token:
		return False

	cred_dir = Path("/etc/letsencrypt")
	cred_dir.mkdir(parents=True, exist_ok=True)
	cred_file = cred_dir / "hostinger.ini"
	cred_file.write_text(f"dns_hostinger_api_token = {token}\n")
	os.chmod(cred_file, 0o600)

	cert_name = f"{base_domain}-wildcard"
	live = CERT_ROOT / cert_name
	cmd = [
		"/opt/certbot-hostinger/bin/certbot",
		"certonly",
		"--authenticator",
		"dns-hostinger",
		"--dns-hostinger-credentials",
		str(cred_file),
		"--non-interactive",
		"--agree-tos",
		"--register-unsafely-without-email",
		"--cert-name",
		cert_name,
		"-d",
		base_domain,
		"-d",
		f"*.{base_domain}",
		"-d",
		f"www.{base_domain}",
	]
	proc = subprocess.run(cmd, capture_output=True, text=True)
	if proc.returncode != 0:
		frappe.log_error(
			title="wildcard certbot failed",
			message=(proc.stdout or "")[-2000:] + "\n" + (proc.stderr or "")[-2000:],
		)
		return False

	cert = str(live / "fullchain.pem")
	key = str(live / "privkey.pem")
	if not (_file_exists(cert) and _file_exists(key)):
		return False

	conf["wildcard"] = {
		"domain": f"*.{base_domain}",
		"ssl_certificate": cert,
		"ssl_certificate_key": key,
	}
	saas_ssl = dict(saas_ssl)
	saas_ssl["mode"] = "wildcard"
	conf["saas_ssl"] = saas_ssl
	(_sites_path() / "common_site_config.json").write_text(json.dumps(conf, indent=1) + "\n")
	return True
