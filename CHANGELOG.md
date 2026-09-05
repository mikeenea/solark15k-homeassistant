# Changelog

All notable project changes will be documented here.

The project is currently in pre-release field-validation status.

## Unreleased

### Added

- Expanded project README and architecture.
- Apache-2.0 licensing boundary and third-party notices.
- Hardware selection and cabling guidance.
- Sol-Ark/SolarAssistant splitter wiring documentation.
- Waveshare 2-channel gateway setup procedure.
- First-inverter commissioning procedure.
- Native Home Assistant Modbus guidance.
- Dual-inverter validation methodology.
- InfluxDB multi-year historian design.
- Grafana dashboard architecture.
- Detailed troubleshooting guide.
- Sol-Ark V1.4 implementation-oriented register CSV.
- Fault-bit reference for documented V1.4 fault bits.
- Dependency-free Python Modbus TCP commissioning probe.
- Initial Home Assistant test package and commissioning dashboard.
- GitHub Actions validation for Python, YAML, and register CSV.
- Repository security and contribution guidelines.
- Project roadmap.
- Field-validation issue for Sol-Ark #1 / Waveshare CH1.

### Known validation items

- Battery power sign convention requires live validation.
- Battery current sign convention requires live validation.
- Battery temperature encoding should be confirmed against current firmware.
- Parallel-inverter register semantics require field classification before aggregation.
- Lifetime energy 32-bit word handling should be compared to inverter totals during commissioning.

## Versioning plan

No stable semantic version has been assigned yet.

Proposed progression:

```text
0.1.0 -> first inverter validated
0.2.0 -> second inverter validated
0.3.0 -> parallel aggregation validated
0.4.0 -> InfluxDB/Grafana baseline complete
1.0.0 -> stable read-only dual-Sol-Ark 15K release
```
