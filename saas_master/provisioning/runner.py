"""Subprocess runner for bench commands.

Adapted from frappe/bench_manager utils.run_command:
- password args redacted from the logged command
- output captured line-by-line into a Provisioning Log document
- returns success flag instead of relying on realtime events
"""

import re
import shlex
import time
from subprocess import PIPE, STDOUT, Popen

import frappe
from frappe.utils import get_bench_path

SENSITIVE_FLAGS = [
	"--mariadb-root-password",
	"--db-root-password",
	"--admin-password",
	"--root-password",
]


def redact(command: str) -> str:
	redacted = command + " "
	for flag in SENSITIVE_FLAGS:
		redacted = re.sub(rf"{flag} \S+ ", f"{flag} ****** ", redacted)
	# positional password: bench --site X set-admin-password <pw>
	redacted = re.sub(r"(set-admin-password) \S+ ", r"\1 ****** ", redacted)
	# password values inside JSON kwargs, e.g. "password": "secret"
	redacted = re.sub(r'(\\?"[a-z_]*password\\?"\s*:\s*\\?")[^"\\]*(\\?")', r"\1******\2", redacted)
	return redacted.strip()


def run_command(command: str, tenant_site: str, step: str, timeout: int = 1800) -> tuple[bool, str]:
	"""Run one shell command from the bench root; log to Provisioning Log.

	Returns (ok, console_output).
	"""
	start = time.time()
	log = frappe.get_doc(
		{
			"doctype": "Provisioning Log",
			"tenant_site": tenant_site,
			"step": step,
			"command": redact(command),
			"status": "Ongoing",
		}
	)
	log.insert(ignore_permissions=True)
	frappe.db.commit()

	lines: list[str] = []
	try:
		proc = Popen(
			shlex.split(command),
			stdin=PIPE,
			stdout=PIPE,
			stderr=STDOUT,
			cwd=get_bench_path(),
			text=True,
		)
		last_flush = time.time()
		for line in iter(proc.stdout.readline, ""):
			# strip progress-bar carriage-return spam
			line = line.split("\r")[-1]
			if line.strip():
				lines.append(line.rstrip("\n"))
			if time.time() - last_flush > 5:
				log.db_set("console", "\n".join(lines[-500:]), commit=True)
				last_flush = time.time()
			if time.time() - start > timeout:
				proc.kill()
				lines.append(f"!! killed after {timeout}s timeout")
				break
		exit_code = proc.wait()
		ok = exit_code == 0
	except Exception as e:
		lines.append(f"!! runner exception: {e}")
		ok = False

	console = "\n".join(lines[-2000:])
	log.db_set("console", console)
	log.db_set("status", "Success" if ok else "Failed")
	log.db_set("time_taken", round(time.time() - start, 1))
	frappe.db.commit()
	return ok, console
