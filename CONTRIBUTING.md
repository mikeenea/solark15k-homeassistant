# Contributing

Thank you for helping validate and improve the Sol-Ark 15K Home Assistant Modbus project.

## Project principles

1. **Read-only first.** Do not add undocumented Modbus writes.
2. **Evidence over assumptions.** Register changes should be supported by documentation or repeatable field observations.
3. **Preserve raw data.** When a decoded value is uncertain, keep the raw register reading available.
4. **One variable at a time.** Troubleshooting and commissioning changes should be isolated.
5. **Parallel systems require validation.** Do not assume a register is per-inverter or system-wide without evidence.

## Before opening an issue

Please review:

- `docs/first-test.md`
- `docs/troubleshooting.md`
- `modbus/solark15k_v1_4_register_map.csv`

## Register-report template

Include the following information:

```text
Inverter model: Sol-Ark 15K
Firmware version:
Standalone or parallel:
Parallel role:
Parallel Modbus SN:
Waveshare model:
Waveshare channel/IP:
Register address:
Raw value:
Decoded value:
Expected value:
Comparison source (LCD, meter, other):
Operating state:
  PV:
  Load:
  Battery charge/discharge:
  Grid import/export:
Notes:
```

## Communication-problem template

```text
Waveshare IP reachable: yes/no
TCP 502 reachable: yes/no
Serial settings: 9600/8/N/1 confirmed yes/no
Protocol mode: Modbus TCP <-> RTU confirmed yes/no
Storage/autopolling disabled: yes/no
Slave ID: 1
A/B continuity checked: yes/no
Ground continuity checked: yes/no
Termination method:
Battery communication: CAN/RS485
BMS Lithium Batt mode:
Python probe output/error:
Home Assistant log excerpt:
```

## Pull requests

For code or configuration changes:

- explain the problem being solved;
- identify the affected register(s);
- include test evidence;
- avoid unrelated formatting changes;
- update documentation when behavior changes;
- do not include secrets, passwords, private IP credentials, or API tokens.

## Home Assistant YAML changes

When changing YAML:

- preserve unique IDs;
- use correct device/state classes;
- avoid silently converting unavailable inputs to zero for critical system totals;
- document sign conventions;
- document any firmware-sensitive scaling;
- run Home Assistant configuration validation before merging when possible.

## Python probe changes

The commissioning probe intentionally uses only the Python standard library. Keep it dependency-free unless there is a compelling reason to change that design.

Do not add write-function support to the commissioning probe.

## InfluxDB/Grafana contributions

Do not commit:

- database credentials;
- tokens;
- passwords;
- private URLs containing secrets;
- personally identifying site information.

Dashboard JSON and query examples should use generic datasource references where possible.

## Third-party material

Do not commit third-party manuals or PDFs unless redistribution rights are clear. Prefer links, citations in documentation, and implementation-oriented tables created for this project.

## Licensing

By contributing original material to this repository, you agree that it may be distributed under the repository's Apache License 2.0 unless explicitly stated otherwise.
