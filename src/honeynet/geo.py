from __future__ import annotations

import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class GeoInfo:
    country: str
    city: str
    latitude: float
    longitude: float
    network_type: str


PRIVATE_GEO = GeoInfo("Lab/Internal", "Private Network", 20.5937, 78.9629, "private")
LOOPBACK_GEO = GeoInfo("Localhost", "Loopback", 0.0, 0.0, "loopback")
UNKNOWN_GEO = GeoInfo("Unknown", "Unresolved", 0.0, 0.0, "public")


PUBLIC_HINTS = [
    ("8.8.8.0/24", GeoInfo("United States", "Mountain View", 37.3861, -122.0839, "public")),
    ("1.1.1.0/24", GeoInfo("Australia", "Research", -33.4940, 143.2104, "public")),
    ("9.9.9.0/24", GeoInfo("United States", "Berkeley", 37.8715, -122.2730, "public")),
]


def enrich_ip(ip: str) -> GeoInfo:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return UNKNOWN_GEO

    if address.is_loopback:
        return LOOPBACK_GEO
    if address.is_private or address.is_link_local:
        return PRIVATE_GEO

    for cidr, info in PUBLIC_HINTS:
        if address in ipaddress.ip_network(cidr):
            return info
    return UNKNOWN_GEO

