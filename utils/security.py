"""
Security utilities for URL validation, filename sanitization, and SSRF protection.
"""
from __future__ import annotations

import ipaddress
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


# Blocked/reserved IP ranges for SSRF protection
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private
    ipaddress.ip_network("172.16.0.0/12"),   # Private
    ipaddress.ip_network("192.168.0.0/16"),  # Private
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local
    ipaddress.ip_network("::1/128"),         # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),        # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),       # IPv6 link-local
    ipaddress.ip_network("0.0.0.0/8"),       # Current network
    ipaddress.ip_network("224.0.0.0/4"),     # Multicast
    ipaddress.ip_network("240.0.0.0/4"),     # Reserved
]

ALLOWED_SCHEMES = {"http", "https"}


def is_private_or_reserved_ip(ip_str: str) -> bool:
    """Check if IP address is in blocked/reserved ranges."""
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in BLOCKED_NETWORKS:
            if ip in network:
                return True
        return False
    except ValueError:
        return True  # Block invalid IPs


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate URL for SSRF protection.
    Returns (is_valid, error_message)
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"
    
    # Check scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, f"Scheme '{parsed.scheme}' not allowed. Only http/https permitted."
    
    # Check hostname exists
    if not parsed.hostname:
        return False, "URL must have a hostname"
    
    hostname = parsed.hostname.lower()
    
    # Block localhost variations
    if hostname in ("localhost", "0.0.0.0", "::1"):
        return False, "Access to localhost is not allowed"
    
    # Try to resolve and check if it's an IP
    try:
        # Check if hostname is already an IP
        ip = ipaddress.ip_address(hostname)
        if is_private_or_reserved_ip(str(ip)):
            return False, "Access to private/reserved IP addresses is not allowed"
    except ValueError:
        # It's a domain name - we'll do DNS resolution check at connection time
        # For now, just basic validation
        pass
    
    # Block common internal service patterns
    if hostname.endswith((".local", ".internal", ".lan", ".corp")):
        return False, "Access to internal domains is not allowed"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and unsafe characters.
    """
    if not filename:
        return "downloaded-file"
    
    # Get just the basename to prevent path traversal
    filename = Path(filename).name
    
    # Remove null bytes and control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Replace path separators and other dangerous chars
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    if not filename or filename in ('.', '..'):
        return "downloaded-file"
    
    # Limit length
    if len(filename) > 255:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:255 - len(ext)] + ext
    
    return filename


def is_safe_path(path: Path, base_dir: Path) -> bool:
    """Check if path is within base directory (prevent path traversal)."""
    try:
        resolved_path = path.resolve()
        resolved_base = base_dir.resolve()
        return str(resolved_path).startswith(str(resolved_base) + str(Path.separator)) or str(resolved_path) == str(resolved_base)
    except Exception:
        return False
