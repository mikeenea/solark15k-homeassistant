# Firmware Compatibility and Validation Matrix

## Purpose

Sol-Ark Modbus behavior can vary by inverter model and firmware revision. This project therefore records the exact firmware versions used during field validation and treats register behavior as firmware-sensitive until proven otherwise.

This file is the authoritative project record for firmware observations.

## Baseline installation

The initial development and commissioning system consists of two parallel Sol-Ark 15K inverters. Both inverters currently report the same software versions:

```text
SW Ver.: M 7.2.2.2 / S 1.7.2.6 / C 1.4.3.F
```

| Inverter | Model | M version | S version | C version | Status |
|---|---|---|---|---|---|
| Sol-Ark #1 | 15K | 7.2.2.2 | 1.7.2.6 | 1.4.3.F | Awaiting Modbus field validation |
| Sol-Ark #2 | 15K | 7.2.2.2 | 1.7.2.6 | 1.4.3.F | Awaiting Modbus field validation |

The exact meaning of the `M`, `S`, and `C` firmware components is not assumed by this project unless Sol-Ark documentation explicitly defines them. We preserve the version string exactly as displayed by the inverter.

## Why firmware version matters

The project register map is initially based on the public Sol-Ark Modbus RTU Protocol V1.4 documentation. A protocol document and inverter firmware are separate versioned artifacts. A register documented in V1.4 may behave differently in later inverter firmware, even if its address remains unchanged.

For that reason, the following are considered **field-validated behavior**, not assumptions:

- register availability;
- scaling factors;
- signed-value direction;
- temperature offsets;
- relay-state encoding;
- fault-bit behavior;
- daily and lifetime counter semantics;
- behavior of registers in a parallel inverter system;
- whether a value is per-inverter, duplicated system-wide, master-only, or slave-only.

## Current validation target

The first validation target is:

```text
Model:       Sol-Ark 15K
Firmware:    M 7.2.2.2 / S 1.7.2.6 / C 1.4.3.F
Protocol:    Sol-Ark Modbus RTU Protocol V1.4
Slave ID:    1
Function:    FC3 Read Holding Registers
Transport:   Waveshare Modbus TCP <-> RTU gateway
Serial:      9600 baud, 8 data bits, no parity, 1 stop bit
```

## Validation matrix

The following table will be updated as live testing is completed.

| Register / Feature | V1.4 documented behavior | Firmware M 7.2.2.2 / S 1.7.2.6 / C 1.4.3.F | Validation state |
|---|---|---|---|
| 79 Grid frequency | uint16 × 0.01 Hz | TBD | Pending |
| 91 Heat-sink temperature | offset temperature encoding | TBD | Pending |
| 103-106 Fault words | four 16-bit fault bitmaps | TBD | Pending |
| 109-114 PV voltage/current | three MPPT channels on 15K | TBD | Pending |
| 150-152 Grid voltages | split-phase L1-N/L2-N/L1-L2 | TBD | Pending |
| 169 Grid total power | positive buy, negative sell | TBD | Pending |
| 175 Inverter total power | signed watts | TBD | Pending |
| 178 Load total power | signed watts | TBD | Pending |
| 182 Battery temperature | raw × 0.1 - 100 °C | TBD | Pending |
| 183 Battery voltage | uint16 × 0.01 V | TBD | Pending |
| 184 Battery SOC | uint16 percent | TBD | Pending |
| 186-188 PV1/PV2/PV3 power | watts | TBD | Pending |
| 190 Battery power | signed watts; direction not defined in V1.4 | TBD | Pending |
| 191 Battery current | signed × 0.01 A; direction not defined in V1.4 | TBD | Pending |
| 194 Grid relay | 1=open, 2=closed | TBD | Pending |
| 195 Generator relay | low nibble state encoding | TBD | Pending |
| 72/73 Battery charge total | 32-bit low/high words | TBD | Pending |
| 74/75 Battery discharge total | 32-bit low/high words | TBD | Pending |
| 78/80 Grid import total | non-contiguous low/high words | TBD | Pending |
| 81/82 Grid export total | 32-bit low/high words | TBD | Pending |
| 85/86 Load total | 32-bit low/high words | TBD | Pending |
| 96/97 PV total | 32-bit low/high words | TBD | Pending |

## Parallel-inverter firmware validation

Both inverters currently have identical firmware. That is useful because it removes firmware mismatch as an initial variable when comparing inverter #1 and inverter #2.

During parallel-system validation, record both units at the same timestamp for at least:

- register 169 — grid total power;
- register 172 — external CT total power;
- register 175 — inverter total power;
- register 178 — load total power;
- register 190 — battery power;
- register 191 — battery current;
- register 108 — daily PV energy;
- registers 76/77 — daily grid import/export;
- register 84 — daily load energy.

Each field will be classified as one of:

```text
PER_INVERTER
SYSTEM_DUPLICATED
MASTER_ONLY
SLAVE_ONLY
TRANSFORMED
UNKNOWN
```

No production aggregation formula should be created until this classification is complete.

## Firmware changes

If either inverter is updated, record the old and new software strings before resuming long-term monitoring.

Recommended process:

1. record the pre-update firmware string;
2. pause or flag the historical data stream at the update time;
3. install the firmware update;
4. record the post-update firmware string;
5. rerun the Modbus probe against the key validation registers;
6. compare scaling and sign behavior with the prior firmware;
7. update this matrix;
8. only then resume normal production assumptions.

For long-term InfluxDB/Grafana use, firmware-change timestamps should be retained as annotations so historical changes can be correlated with firmware revisions.

## Compatibility reports from other users

Contributors should provide all of the following when reporting register behavior:

```text
Inverter model:
Firmware M:
Firmware S:
Firmware C:
Parallel or standalone:
Master/slave role if parallel:
Battery communications: CAN / RS485 / none
Gateway model:
Gateway mode:
Register address:
Raw register value:
Decoded value:
Expected/displayed inverter value:
Observed timestamp:
```

Reports without firmware identification may still be useful, but they should not be treated as confirmed compatibility evidence.
