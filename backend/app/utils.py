# backend/app/utils.py
from urllib.parse import urlparse, urlunparse
import tldextract
import ipaddress

def ensure_scheme(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("Empty URL")
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url

def normalize_url(url: str) -> str:
    """Return a normalized URL: scheme + lower host (no trailing slash) + path (no fragment/query)."""
    url = ensure_scheme(url)
    p = urlparse(url)
    netloc = p.netloc.lower()
    # remove default ports
    if netloc.endswith(":80"):
        netloc = netloc[:-3]
    # remove fragments and queries for normalization
    normalized = urlunparse((p.scheme, netloc, p.path.rstrip('/'), '', '', ''))
    return normalized

def extract_domain_parts(url: str):
    url = ensure_scheme(url)
    p = urlparse(url)
    host = p.netloc.split('@')[-1].split(':')[0]
    # tldextract gives subdomain, domain, suffix
    te = tldextract.extract(host)
    domain = te.domain + (('.' + te.suffix) if te.suffix else '')
    subdomain = te.subdomain
    path = p.path
    return {
        "host": host,
        "domain": domain,
        "subdomain": subdomain,
        "path": path
    }

def is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except Exception:
        return False
from difflib import get_close_matches, SequenceMatcher

def hostname_similarity(a, b):
    """Returns a percentage similarity between two hostnames."""
    return round(SequenceMatcher(None, a, b).ratio() * 100, 2)

def suggest_closest_whitelist(url: str, whitelist, n=1, cutoff=0.6):
    """
    Suggests the closest matching official domain from the whitelist.

    :param url: URL entered by the user (str)
    :param whitelist: List of dicts with 'domain' and 'canonical_url'
    :param n: Number of suggestions to return
    :param cutoff: Similarity threshold (0 to 1)
    :return: Dict with 'suggested_url' and 'similarity', or None
    """
    # Extract hostname from URL
    hostname = url.lower().replace("http://", "").replace("https://", "").split("/")[0]

    # List of whitelist domains
    whitelist_domains = [w["domain"] for w in whitelist]

    # Get closest matches
    matches = get_close_matches(hostname, whitelist_domains, n=n, cutoff=cutoff)

    if matches:
        best_match = matches[0]
        canonical_url = next((w["canonical_url"] for w in whitelist if w["domain"] == best_match), None)
        return {"suggested_url": canonical_url, "similarity": hostname_similarity(hostname, best_match)}

    return None
def extract_features(url: str):
    """Extract simple lexical features from URL."""
    num_dots = url.count(".")
    url_len = len(url)
    num_dash = url.count("-")
    has_at = int("@" in url)
    has_https = int(url.startswith("https"))
    return [[num_dots, url_len, num_dash, has_at, has_https]]
