# Installation Checklist

Use this as a print-friendly commissioning checklist for the physical build.

## Current deployment status — 2026-09-05

Software staging is complete through Home Assistant. Field commissioning is paused until the Waveshare 2-CH RS485 TO POE ETH (B) gateway is available.

Completed before the hold point:

- [x] Home Assistant package support enabled.
- [x] `solark15k_test_package.yaml` copied into the Home Assistant packages folder.
- [x] Home Assistant configuration check passes.
- [x] Home Assistant restarted successfully with the package loaded.
- [x] `sensor.sol_ark_test_*` entities are present.
- [x] InfluxDB OSS 2.8 installed.
- [x] Clean `solark` bucket created.
- [x] InfluxDB export restricted to project-created Sol-Ark entities and project formulas only.
- [x] Grafana installed.
- [x] Grafana InfluxDB data source connection tested successfully.
- [ ] Waveshare hardware procured/installed.
- [ ] Live Modbus values received.

Until the Waveshare is installed, Sol-Ark test entities may remain `unknown`; this is expected and is not a reason to troubleshoot the register map or Grafana.

## A. Pre-installation

- [x] Confirm repository test package is current.
- [x] Confirm Sol-Ark model is 15K.
- [ ] Record inverter #1 serial number.
- [ ] Record inverter #2 serial number.
- [x] Record inverter firmware versions.
- [ ] Record parallel master/slave roles.
- [ ] Record Parallel-screen Modbus SN values for reference only.
- [ ] Confirm battery communication protocol is CAN.
- [ ] Confirm `BMS Lithium Batt` mode is `00`.
- [ ] Photograph/document existing splitter connections.

## B. Hardware inventory

- [ ] Waveshare 2-CH RS485 TO POE ETH (B).
- [ ] PoE switch/injector available.
- [ ] Two passive RJ45 patch leads.
- [ ] Multimeter.
- [ ] Labels/heat-shrink as desired.
- [ ] 120-ohm termination components if required.
- [ ] Laptop/PC with Ethernet/Wi-Fi access to the gateway network.
- [ ] Python 3 available for probe test.

## C. Cable preparation

### Sol-Ark #1

- [ ] RJ45 pin 1 conductor identified and labeled `B`.
- [ ] RJ45 pin 2 conductor identified and labeled `A`.
- [ ] RJ45 pin 3 conductor identified and labeled `GND`.
- [ ] No short A-B.
- [ ] No short A-GND.
- [ ] No short B-GND.

### Sol-Ark #2

- [ ] RJ45 pin 1 conductor identified and labeled `B`.
- [ ] RJ45 pin 2 conductor identified and labeled `A`.
- [ ] RJ45 pin 3 conductor identified and labeled `GND`.
- [ ] No short A-B.
- [ ] No short A-GND.
- [ ] No short B-GND.

## D. Waveshare CH1 configuration

- [ ] Static/reserved IP selected: ____________________
- [ ] Subnet mask: ____________________
- [ ] Gateway: ____________________
- [ ] TCP port: 502
- [ ] Modbus TCP ↔ RTU mode selected.
- [ ] Non-storage mode selected.
- [ ] Baud: 9600.
- [ ] Data bits: 8.
- [ ] Parity: None.
- [ ] Stop bits: 1.
- [ ] Termination method documented: ____________________

## E. CH1 wiring

- [ ] Sol-Ark #1 splitter RS485 pin 1 -> CH1 B-.
- [ ] Sol-Ark #1 splitter RS485 pin 2 -> CH1 A+.
- [ ] Sol-Ark #1 splitter RS485 pin 3 -> CH1 GND.
- [ ] Battery CAN side unchanged.
- [ ] Cable labeled at both ends.

## F. CH1 network test

Run:

```powershell
Test-NetConnection <CH1-IP> -Port 502
```

- [ ] `TcpTestSucceeded : True`.

## G. CH1 Modbus probe

Run:

```powershell
python tools/solark_modbus_probe.py <CH1-IP>
```

- [ ] Read succeeds.
- [ ] Battery voltage plausible.
- [ ] Battery SOC plausible.
- [ ] Grid voltages plausible.
- [ ] Grid frequency plausible.
- [ ] PV power plausible.
- [ ] Load power plausible.
- [ ] Fault words recorded.

Run raw dump:

```powershell
python tools/solark_modbus_probe.py <CH1-IP> --dump
```

- [ ] Raw dump saved locally.

## H. CH1 field validation

- [ ] Grid power sign confirmed during import.
- [ ] Grid power sign confirmed during export if available.
- [ ] Battery power sign confirmed during charge.
- [ ] Battery power sign confirmed during discharge.
- [ ] Battery current sign confirmed during charge.
- [ ] Battery current sign confirmed during discharge.
- [ ] Battery temperature scaling confirmed.
- [ ] Heat-sink temperature scaling confirmed.
- [ ] Lifetime energy counters compared with inverter totals.

## I. Home Assistant CH1

- [x] Test package copied to HA.
- [ ] Host IP edited to the actual Waveshare address.
- [x] HA configuration check passes.
- [x] HA restarted.
- [x] Sol-Ark test entities are created.
- [ ] Core sensors populate with live values.
- [ ] Any Fault sensor behaves correctly.
- [ ] 24-hour stability period started.
- [ ] 24-hour stability period passed.

## J. Waveshare CH2 configuration

Do not start until CH1 is validated.

- [ ] Static/reserved IP selected: ____________________
- [ ] TCP port: 502.
- [ ] Modbus TCP ↔ RTU mode.
- [ ] Non-storage mode.
- [ ] 9600/8/N/1.
- [ ] Termination method documented.

## K. CH2 wiring and validation

- [ ] Sol-Ark #2 splitter pin 1 -> CH2 B-.
- [ ] Sol-Ark #2 splitter pin 2 -> CH2 A+.
- [ ] Sol-Ark #2 splitter pin 3 -> CH2 GND.
- [ ] Battery CAN side unchanged.
- [ ] TCP 502 test passes.
- [ ] Python probe passes.
- [ ] Raw dump captured.
- [ ] Core values validated.
- [ ] 24-hour stability period passed.

## L. Parallel-system classification

For each register, mark one:

```text
PER_INVERTER / SYSTEM_DUPLICATED / MASTER_ONLY / SLAVE_ONLY / UNKNOWN
```

- [ ] 169 Grid total power: ____________________
- [ ] 172 External CT total: ____________________
- [ ] 175 Inverter total power: ____________________
- [ ] 178 Load total power: ____________________
- [ ] 190 Battery power: ____________________
- [ ] 191 Battery current: ____________________
- [ ] 108 Daily PV energy: ____________________
- [ ] 76/77 Daily grid import/export: ____________________
- [ ] 84 Daily load energy: ____________________
- [ ] 96/97 Lifetime PV: ____________________

## M. Production readiness

- [ ] Both channels stable.
- [ ] Parallel aggregation validated.
- [ ] Production HA package built.
- [x] InfluxDB installed and clean project bucket created.
- [x] Grafana installed and connected to InfluxDB.
- [ ] InfluxDB export receiving verified live Sol-Ark entities.
- [ ] Grafana baseline dashboard deployed.
- [ ] Backup process documented and tested.
- [x] GitHub issue #1 updated with current commissioning status.
