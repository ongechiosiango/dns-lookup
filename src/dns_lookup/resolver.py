"""Resolve DNS records using dnspython.

We normalize every record type into a plain dict of strings so callers
and tests never need to know about dnspython internals:

    {
        "A":     ["93.184.216.34"],
        "AAAA":  ["2606:2800:220:1:248:1893:25c8:1946"],
        "MX":    ["10 mail.example.com."],
        "TXT":   ["v=spf1 -all"],
        "NS":    ["a.iana-servers.net."],
        "CNAME": ["example.com."],
    }
"""

from __future__ import annotations

from typing import Callable, Dict, List

import dns.exception
import dns.resolver

# Record types we support. Order determines display order.
SUPPORTED_TYPES = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA"]


class LookupError(Exception):
    """Raised when a DNS lookup fails for a name."""


def _format_rdata(rdtype: str, rdata) -> str:
    """Convert a dnspython rdata object into a readable string."""
    if rdtype == "MX":
        return f"{rdata.preference} {rdata.exchange.to_text()}"
    if rdtype == "SOA":
        return (
            f"{rdata.mname.to_text()} {rdata.rname.to_text()} "
            f"serial={rdata.serial} refresh={rdata.refresh} "
            f"retry={rdata.retry} expire={rdata.expire} minimum={rdata.minimum}"
        )
    return rdata.to_text()


def resolve(
    name: str,
    record_types: List[str] = None,
    resolver=None,
    timeout: float = 5.0,
) -> Dict[str, List[str]]:
    """Resolve a name against the given record types.

    Args:
        name: the domain to look up (e.g. "github.com").
        record_types: list of types to query. Defaults to SUPPORTED_TYPES.
        resolver: optional dns.resolver.Resolver (used for tests).
        timeout: per-query timeout in seconds.

    Returns:
        A dict mapping record type -> list of string values. Types with
        no records are omitted from the result.
    """
    if not name or not name.strip():
        raise LookupError("Name cannot be empty.")

    name = name.strip()
    types = [t.upper() for t in (record_types or SUPPORTED_TYPES)]

    if resolver is None:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = timeout
        resolver.timeout = timeout

    results: Dict[str, List[str]] = {}

    for rdtype in types:
        try:
            answers = resolver.resolve(name, rdtype)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            continue
        except dns.exception.Timeout:
            raise LookupError(f"Timed out resolving {rdtype} for {name}.")
        except dns.exception.DNSException as exc:
            raise LookupError(f"DNS error for {name} {rdtype}: {exc}") from exc

        values = [_format_rdata(rdtype, r) for r in answers]
        if values:
            results[rdtype] = values

    if not results:
        raise LookupError(f"No records found for {name}.")

    return results
