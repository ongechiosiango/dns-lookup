# Usage Guide

## Basic lookup

    dns-lookup github.com

Queries A, AAAA, CNAME, MX, NS, TXT, and SOA records in one pass and
prints a table per record type that returned results.

## Only certain types

    dns-lookup github.com --type A --type MX

Or shorthand:

    dns-lookup github.com -t MX

## JSON output (for scripting)

    dns-lookup github.com --json

## Custom timeout

    dns-lookup slow.example.com --timeout 10

## Supported record types

A, AAAA, CNAME, MX, NS, TXT, SOA

## Exit codes

- 0 - at least one record was resolved
- 1 - lookup failed, invalid type, or empty result
