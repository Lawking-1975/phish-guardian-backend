# backend/app/utils.py
from urllib.parse import urlparse, urlunparse
import tldextract
import ipaddress
from difflib import get_close_matches, SequenceMatcher
import pandas as pd
# -------------------------
# URL Normalization
# -------------------------
def ensure_scheme(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("Empty URL")
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url

def normalize_url(url: str) -> str:
    url = ensure_scheme(url)
    p = urlparse(url)
    netloc = p.netloc.lower()
    if netloc.endswith(":80"):
        netloc = netloc[:-3]
    normalized = urlunparse((p.scheme, netloc, p.path.rstrip('/'), '', '', ''))
    return normalized

def extract_domain_parts(url: str):
    url = ensure_scheme(url)
    p = urlparse(url)
    host = p.netloc.split('@')[-1].split(':')[0]
    te = tldextract.extract(host)
    domain = te.domain + (('.' + te.suffix) if te.suffix else '')
    subdomain = te.subdomain
    path = p.path
    return {"host": host, "domain": domain, "subdomain": subdomain, "path": path}

def is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

# -------------------------
# Lexical similarity
# -------------------------
def hostname_similarity(a, b):
    return round(SequenceMatcher(None, a, b).ratio() * 100, 2)

def suggest_closest_whitelist(url: str, whitelist, n=1, cutoff=0.6):
    hostname = url.lower().replace("http://", "").replace("https://", "").split("/")[0]
    whitelist_domains = [w["domain"] for w in whitelist]
    matches = get_close_matches(hostname, whitelist_domains, n=n, cutoff=cutoff)
    if matches:
        best_match = matches[0]
        canonical_url = next((w["canonical_url"] for w in whitelist if w["domain"] == best_match), None)
        return {"suggested_url": canonical_url, "similarity": hostname_similarity(hostname, best_match)}
    return None

# -------------------------
# Feature extraction for ML
# -------------------------
FEATURE_COLUMNS = [
    "length", "has_ip", "num_dots", "num_hyphens", "contains_https",
    # add all columns used when training the model
]
def extract_features(url: str):
    num_dots = url.count(".")
    url_len = len(url)
    num_dash = url.count("-")
    has_at = int("@" in url)
    has_https = int(url.startswith("https"))
    return [[num_dots, url_len, num_dash, has_at, has_https]]
