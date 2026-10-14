"""Tests for the DNS resolver using a fake resolver (no live DNS)."""

from __future__ import annotations

import dns.exception
import dns.resolver
import pytest

from dns_lookup.resolver import LookupError, resolve


class FakeRdata:
    """Mimic dnspython rdata objects with a to_text() method."""

    def __init__(self, text: str):
        self._text = text

    def to_text(self) -> str:
        return self._text


class FakeMX:
    def __init__(self, preference: int, exchange: str):
        self.preference = preference
        self.exchange = FakeRdata(exchange)

    def to_text(self) -> str:
        return f"{self.preference} {self.exchange.to_text()}"


class FakeSOA:
    def __init__(self, mname, rname, serial, refresh, retry, expire, minimum):
        self.mname = FakeRdata(mname)
        self.rname = FakeRdata(rname)
        self.serial = serial
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.minimum = minimum

    def to_text(self) -> str:
        return "soa"


class FakeResolver:
    """Return canned answers per (name, rdtype) pair."""

    def __init__(self, responses):
        # responses: dict[(name, rdtype)] -> list of rdata or Exception
        self.responses = responses

    def resolve(self, name, rdtype):
        key = (name, rdtype)
        if key not in self.responses:
            raise dns.resolver.NoAnswer()
        value = self.responses[key]
        if isinstance(value, Exception):
            raise value
        return value


def test_resolve_a_record():
    fake = FakeResolver({
        ("example.com", "A"): [FakeRdata("93.184.216.34")],
    })
    result = resolve("example.com", record_types=["A"], resolver=fake)
    assert result == {"A": ["93.184.216.34"]}


def test_resolve_multiple_types():
    fake = FakeResolver({
        ("example.com", "A"): [FakeRdata("93.184.216.34")],
        ("example.com", "MX"): [FakeMX(10, "mail.example.com.")],
    })
    result = resolve("example.com", record_types=["A", "MX"], resolver=fake)
    assert result["A"] == ["93.184.216.34"]
    assert result["MX"] == ["10 mail.example.com."]


def test_resolve_skips_missing_types():
    """NoAnswer means the type exists but has no records — omit it."""
    fake = FakeResolver({
        ("example.com", "A"): [FakeRdata("93.184.216.34")],
        # AAAA missing -> NoAnswer -> omitted
    })
    result = resolve("example.com", record_types=["A", "AAAA"], resolver=fake)
    assert result == {"A": ["93.184.216.34"]}


def test_resolve_raises_when_no_records_at_all():
    fake = FakeResolver({})
    with pytest.raises(LookupError, match="No records found"):
        resolve("nope.example", record_types=["A"], resolver=fake)


def test_resolve_rejects_empty_name():
    fake = FakeResolver({})
    with pytest.raises(LookupError, match="empty"):
        resolve("", record_types=["A"], resolver=fake)


def test_resolve_handles_timeout():
    fake = FakeResolver({
        ("slow.example", "A"): dns.exception.Timeout(),
    })
    with pytest.raises(LookupError, match="Timed out"):
        resolve("slow.example", record_types=["A"], resolver=fake)


def test_resolve_lowercase_type_normalized():
    fake = FakeResolver({
        ("example.com", "A"): [FakeRdata("1.2.3.4")],
    })
    result = resolve("example.com", record_types=["a"], resolver=fake)
    assert result == {"A": ["1.2.3.4"]}


def test_resolve_strips_whitespace_from_name():
    fake = FakeResolver({
        ("example.com", "A"): [FakeRdata("1.2.3.4")],
    })
    result = resolve("  example.com  ", record_types=["A"], resolver=fake)
    assert result == {"A": ["1.2.3.4"]}
