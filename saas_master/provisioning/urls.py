"""Public access URLs for tenant stores (DNS multitenant + HTTPS)."""

PUBLIC_IP = "167.99.228.61"
# Master (signup / landing) — always port 80 / 443
MASTER_PORT = 80
# Tenant preview fallback: cookie-selected site via ?site= (legacy IP mode)
TENANT_PORT = 8081


def master_url(path: str = "/") -> str:
	return f"https://flexloopers.com{path}"


def tenant_url(site_name: str) -> str:
	"""Canonical HTTPS URL for a tenant store under DNS multitenant."""
	return f"https://{site_name}"


def tenant_ip_url(site_name: str) -> str:
	"""Legacy clickable IP link that opens a specific tenant store (port 8081)."""
	return f"http://{PUBLIC_IP}:{TENANT_PORT}/?site={site_name}"
