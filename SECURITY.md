# Security Policy

## Scope

This project connects Home Assistant to power-conversion equipment through a Modbus TCP gateway. Although the current design is read-only, the network path reaches equipment that participates in the site's electrical system.

## Security principles

- Keep Modbus TCP on trusted networks.
- Do not expose TCP port 502 directly to the public Internet.
- Do not publish Waveshare management credentials.
- Do not commit Home Assistant secrets, InfluxDB tokens, Grafana credentials, or private certificates.
- Do not add undocumented Modbus writes.
- Treat proposed write support as a separate safety/security review item.

## Repository secrets

Never commit:

```text
secrets.yaml
InfluxDB API tokens
Grafana API keys
GitHub personal access tokens
Waveshare passwords
VPN credentials
SSH private keys
TLS private keys
full Home Assistant backups
```

Use Home Assistant `secrets.yaml`, environment variables, or platform-native secret stores as appropriate.

## Network segmentation

Recommended design:

```text
Sol-Ark RS485
    |
Waveshare gateway
    |
Trusted infrastructure / IoT VLAN
    |
Firewall/routing policy
    |
Home Assistant
```

Permit only the traffic required for operation and administration.

## Public repository hygiene

Before posting logs or screenshots, remove or mask:

- public IP addresses;
- passwords/tokens;
- Wi-Fi credentials;
- personally identifying location details if not intentionally public;
- unrelated device identifiers;
- sensitive internal hostnames.

Private RFC1918 addresses are not generally secrets, but contributors may still choose to sanitize them.

## Modbus write policy

The current repository is intentionally read-only. Any future proposal to add write support should include:

1. authoritative documentation for the writable register;
2. accepted value/range definitions;
3. failure-mode analysis;
4. rollback/recovery procedure;
5. explicit enable/disable control;
6. protection against accidental writes;
7. field testing on non-critical settings first;
8. documentation warning that inverter configuration changes can affect electrical operation.

Undocumented or guessed writes should not be merged.

## Reporting a security concern

If a concern could expose credentials or enable unsafe control, do not post secrets in a public issue. Open a minimal issue describing the category without sensitive details, or use GitHub's private vulnerability-reporting mechanism if enabled for the repository.
