# First Test and Commissioning Procedure

## Purpose

This procedure validates the complete data path from one Sol-Ark 15K through one Waveshare RS485 channel before Home Assistant is asked to monitor the inverter continuously.

Do not begin with both inverters connected. Establish a known-good single-channel baseline first.

## Prerequisites

Before testing:

- Sol-Ark 15K is operational.
- Battery communication uses CAN, not RS485.
- `BMS Lithium Batt` mode is `00`.
- Existing splitter remains connected to the Battery CAN Bus port.
- Battery CAN side remains unchanged.
- Splitter RS485 output is connected to Waveshare CH1.
- Waveshare CH1 is configured for Modbus TCP ↔ RTU.
- CH1 serial parameters are 9600/8/N/1.
- CH1 TCP port is 502.
- Gateway is in non-storage mode.
- Signal ground is connected.
- Correct RS485 termination is present.

## Stage 1: verify Ethernet reachability

From Windows PowerShell:

```powershell
Test-NetConnection 192.168.1.241 -Port 502
```

Replace the IP address with the actual CH1 address.

Expected:

```text
TcpTestSucceeded : True
```

If false, stop. Do not troubleshoot RS485 until the TCP endpoint itself is reachable.

## Stage 2: run the no-dependency Modbus probe

The repository includes:

```text
tools/solark_modbus_probe.py
```

It uses only the Python standard library.

Run:

```powershell
python solark_modbus_probe.py 192.168.1.241
```

For a full raw dump:

```powershell
python solark_modbus_probe.py 192.168.1.241 --dump
```

The probe uses:

```text
Unit/slave ID: 1
Function code: 3
Operation: Read Holding Registers
```

No write operation is implemented.

## Stage 3: compare with inverter display

Record the probe output and compare it to the Sol-Ark screen at approximately the same moment.

Priority comparisons:

| Measurement | Register | Expected behavior |
|---|---:|---|
| Battery voltage | 183 | approximately 40-60 V on a 48 V system |
| Battery SOC | 184 | 0-100% |
| Grid L1-N voltage | 150 | approximately 120 V in a normal split-phase system |
| Grid L2-N voltage | 151 | approximately 120 V |
| Grid L1-L2 voltage | 152 | approximately 240 V |
| Grid frequency | 79 | approximately 60 Hz in North America |
| PV1 power | 186 | depends on sunlight |
| PV2 power | 187 | depends on sunlight |
| PV3 power | 188 | applies to 15K |
| Grid total power | 169 | positive buy, negative sell per V1.4 |
| Inverter total power | 175 | signed W |
| Load total power | 178 | signed W |
| Battery power | 190 | signed; charge/discharge sign requires field validation |
| Battery current | 191 | signed; charge/discharge sign requires field validation |

## Stage 4: validate temperature encoding

The V1.4 map documents register 182 battery temperature with a +1000 raw offset:

```text
raw 1200 -> 20.0 C
```

So the initial interpretation is:

```text
Temperature C = raw * 0.1 - 100
```

Register 91 heat-sink temperature uses the same style of offset according to the map.

Compare both values to the inverter's displayed temperatures. If current firmware behaves differently, preserve the raw register reading and open an issue before changing the project-wide formula.

## Stage 5: validate signed power direction

### Grid power register 169

The V1.4 map explicitly defines:

```text
positive = BUY / import
negative = SELL / export
```

Observe a period of known grid import or export and confirm the sign.

### Battery registers 190 and 191

The map labels these as signed but does not explicitly define which sign represents charging versus discharging.

Record:

```text
Time:
Battery state: charging / discharging
Sol-Ark display power:
Register 190 raw/signed:
Register 191 raw/signed:
```

Do not create charge/discharge automations until this sign convention is validated.

## Stage 6: validate energy counters

The V1.4 map includes daily and lifetime counters. Of particular importance:

- total battery charge: 72 low / 73 high;
- total battery discharge: 74 low / 75 high;
- total grid buy: 78 low / 80 high;
- total grid sell: 81 low / 82 high;
- total load: 85 low / 86 high;
- total PV: 96 low / 97 high.

Total grid buy is unusual because register 79, grid frequency, sits between the low and high words. Do not read register 78 as a normal contiguous uint32.

## Stage 7: Home Assistant test package

After the Python probe produces plausible values, copy:

```text
homeassistant/packages/solark15k_test_package.yaml
```

into your Home Assistant packages directory and edit:

```yaml
host: 192.168.1.241
```

to the actual CH1 IP.

If Home Assistant packages are not enabled, merge this into the existing `homeassistant:` section of `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Do not create a duplicate `homeassistant:` key.

Run Home Assistant's configuration check before restart.

## Stage 8: observe stability

Leave the single-inverter test running long enough to observe:

- normal daytime PV ramp;
- battery charging;
- battery discharging;
- grid import/export if available;
- load changes;
- overnight operation;
- Home Assistant restart/reconnect behavior.

Recommended initial stability period: at least 24 hours before enabling the second inverter.

## Stage 9: add inverter #2

Only after inverter #1 is stable:

1. connect Sol-Ark #2 splitter RS485 output to Waveshare CH2;
2. assign CH2 a different IP address;
3. apply the same 9600/8/N/1 and Modbus TCP ↔ RTU settings;
4. use slave ID 1 again;
5. run the Python probe against CH2;
6. compare values with inverter #2 display;
7. repeat the same validation process.

## Stage 10: parallel-system validation

Before adding combined sensors, capture these values from both inverters at the same timestamp:

```text
Grid total power 169
CT total power 172
Inverter total power 175
Load total power 178
Battery power 190
Battery current 191
Daily PV energy 108
Daily grid import/export 76/77
Daily load energy 84
```

Compare to the system/master display. Determine whether each measurement is:

- per inverter;
- duplicated system-wide;
- master-only;
- otherwise transformed by parallel operation.

Only then define aggregation formulas.

## Failure triage order

If the Python probe fails:

1. verify TCP 502 reachability;
2. verify gateway protocol mode;
3. verify 9600/8/N/1;
4. verify slave ID 1;
5. verify A/B continuity;
6. verify GND continuity;
7. verify termination;
8. verify BMS Lithium Batt mode 00;
9. verify battery uses CAN and not RS485;
10. only then test an A/B swap if labeling inconsistency is suspected.

## Commissioning record

Create an issue or local record containing:

```text
Date:
Inverter serial:
Firmware:
Parallel role:
Parallel Modbus SN:
Waveshare channel:
Waveshare IP:
Termination method:
Probe result:
Battery power sign:
Battery current sign:
Battery temperature raw/interpreted:
24-hour stability result:
Notes:
```

This information will help build a firmware/register compatibility matrix over time.
