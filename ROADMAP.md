# Roadmap

## Phase 0 - Repository foundation

- [x] Apache-2.0 licensing
- [x] Project README
- [x] Architecture documentation
- [x] Hardware and wiring documentation
- [x] Waveshare commissioning guidance
- [x] Native Home Assistant first-test package
- [x] Standalone read-only Python Modbus probe
- [x] V1.4 implementation-oriented register table
- [x] Fault-bit reference
- [x] InfluxDB historian design
- [x] Grafana dashboard plan
- [x] Initial field-validation issue

## Phase 1 - Sol-Ark #1 field validation

- [ ] Install Waveshare 2-CH RS485 TO POE ETH (B)
- [ ] Verify splitter RS485 wiring
- [ ] Verify master-side termination
- [ ] Confirm CH1 TCP 502 connectivity
- [ ] Run Python probe
- [ ] Capture raw register dump
- [ ] Compare core values with Sol-Ark display
- [ ] Confirm battery temperature encoding
- [ ] Confirm battery power sign
- [ ] Confirm battery current sign
- [ ] Confirm energy-counter word ordering
- [ ] Run HA test package for 24+ hours

Tracking issue: #1

## Phase 2 - Sol-Ark #2 validation

- [ ] Configure Waveshare CH2
- [ ] Run standalone probe against inverter #2
- [ ] Validate the same register set
- [ ] Run 24+ hour stability test
- [ ] Document firmware/behavior differences, if any

## Phase 3 - Parallel-inverter semantics

- [ ] Classify register 169 grid power
- [ ] Classify register 172 CT total
- [ ] Classify register 175 inverter output
- [ ] Classify register 178 load power
- [ ] Classify registers 190/191 battery power/current
- [ ] Classify daily and lifetime energy counters
- [ ] Determine authoritative source for duplicated system values
- [ ] Build validated combined system sensors

## Phase 4 - Production Home Assistant package

- [ ] Replace `Sol-Ark Test` naming with production per-inverter names
- [ ] Add complete L1/L2 current and power sensors
- [ ] Add availability sensors
- [ ] Add decoded fault binary sensors
- [ ] Add grid import/export templates
- [ ] Add battery charge/discharge templates after sign validation
- [ ] Add validated system totals
- [ ] Add Energy Dashboard-ready entities
- [ ] Add entity categories where appropriate
- [ ] Document migration from test package

## Phase 5 - Long-term historian

- [ ] Configure InfluxDB export include list
- [ ] Validate ingestion and timestamps
- [ ] Define raw retention window
- [ ] Define 1-minute downsample retention
- [ ] Define 15-minute/hourly/day summaries
- [ ] Implement database backup plan
- [ ] Add selected historical query sensors to Home Assistant

## Phase 6 - Grafana dashboards

- [ ] System overview
- [ ] Dual-inverter balance
- [ ] PV/MPPT performance
- [ ] Battery
- [ ] Grid
- [ ] Generator/AC-coupled
- [ ] Fault/event timeline
- [ ] Monthly/yearly energy
- [ ] Year-over-year comparison
- [ ] Store dashboard JSON in repository

## Phase 7 - Event analytics

- [ ] Grid outage detection
- [ ] Outage duration tracking
- [ ] Battery SOC at outage start/end
- [ ] Generator runtime during outage
- [ ] Fault snapshot automation
- [ ] Fault/event history in InfluxDB
- [ ] Inverter imbalance diagnostics
- [ ] MPPT underperformance detection

## Phase 8 - Compatibility and quality

- [ ] Firmware compatibility table
- [ ] Community validation reports
- [ ] Automated YAML/Python validation in CI
- [ ] Register-map unit tests
- [ ] Optional Modbus response replay tests
- [ ] Release/versioning policy
- [ ] First tagged stable release

## Explicitly out of scope for initial releases

- undocumented Modbus writes;
- remote inverter configuration changes;
- cloud-control replacement;
- exposing TCP 502 to the public Internet.

These may be reconsidered only if supported by authoritative documentation and accompanied by an explicit safety review.
