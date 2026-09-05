# Dual-Inverter Deployment

## Purpose

This document covers expansion from a proven single-inverter Modbus connection to two parallel Sol-Ark 15K inverters.

The key rule is simple: **validate each inverter independently before creating system-level combined sensors**.

## Physical topology

```text
Sol-Ark #1 splitter RS485 -> Waveshare CH1 -> IP A:502 -> HA hub solark_1
Sol-Ark #2 splitter RS485 -> Waveshare CH2 -> IP B:502 -> HA hub solark_2
```

Each inverter remains on its own RS485 channel.

## Slave addressing

The public V1.4 map states that this protocol uses slave ID `0x01` and that the Parallel-screen Modbus SN does not change that slave ID.

Therefore both independently connected inverters use:

```text
slave: 1
```

They are distinguished by the separate Waveshare channel IP addresses.

## Why not sum immediately

In a parallel system, some registers may be:

- local to each inverter;
- duplicated on both inverters;
- reported only by the master;
- calculated as a system-wide value by firmware.

Blindly summing duplicated system values would double-count power and energy.

## Validation matrix

Capture simultaneous values from inverter #1, inverter #2, and the Sol-Ark system display.

| Register | Measurement | Validation question |
|---:|---|---|
| 169 | Grid total power | per inverter or system-wide? |
| 172 | External CT total power | duplicated CT reading or per inverter? |
| 175 | Inverter total power | likely per inverter; verify |
| 178 | Load total power | per inverter or system-wide? |
| 190 | Battery power | local conversion path or total bank? |
| 191 | Battery current | local or system-wide? |
| 108 | Daily PV energy | per inverter? |
| 76/77 | Daily grid import/export | per inverter or duplicated? |
| 84 | Daily load energy | per inverter or system-wide? |
| 96/97 | Lifetime PV | per inverter? |

## Suggested validation procedure

Perform several operating states:

### State A: moderate daytime PV

Record:

```text
PV #1
PV #2
Inverter output #1
Inverter output #2
System PV/output on LCD
```

### State B: battery charging

Record:

```text
Battery power #1
Battery power #2
Battery current #1
Battery current #2
System battery power/current
```

### State C: battery discharging

Repeat the same readings and verify sign direction.

### State D: grid import

Record register 169 from both inverters and the system display.

### State E: grid export

Repeat while exporting if possible.

### State F: large load

Observe load registers 176-178 on both inverters and compare to actual/system load.

## Classification outcomes

For each register, classify it as one of:

```text
PER_INVERTER
SYSTEM_DUPLICATED
MASTER_ONLY
SLAVE_ONLY
UNKNOWN
```

Record the classification in an issue or future compatibility table.

## System-level templates

Only values classified as `PER_INVERTER` should normally be summed.

Example for total inverter output after validation:

```yaml
template:
  - sensor:
      - name: "Sol-Ark System Inverter Power"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: >
          {{ states('sensor.sol_ark_1_inverter_total_power') | float(0)
           + states('sensor.sol_ark_2_inverter_total_power') | float(0) }}
```

Example for system PV after confirming each inverter's PV registers are local:

```yaml
      - name: "Sol-Ark System PV Power"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: >
          {{ states('sensor.sol_ark_1_total_pv_power') | float(0)
           + states('sensor.sol_ark_2_total_pv_power') | float(0) }}
```

## Duplicated values

If both inverters report the same system-wide CT value, do not sum them. Instead:

- select the master as authoritative; or
- create a consistency check comparing both values.

Example consistency sensor concept:

```text
abs(CT master - CT slave) < tolerance
```

A disagreement could become a diagnostic indicator.

## Availability handling

System templates should not silently convert an unavailable inverter to zero during normal operation unless that behavior is explicitly desired.

Prefer availability templates requiring both inputs when the quantity truly depends on both inverters.

## Failover considerations

If one inverter or one Waveshare channel goes offline, retain individual entities so Home Assistant clearly shows which source failed.

Potential diagnostic entities:

```text
binary_sensor.sol_ark_1_modbus_online
binary_sensor.sol_ark_2_modbus_online
binary_sensor.sol_ark_parallel_data_consistent
```

These can be added after the first field deployment.

## Historical data tags

When exporting to InfluxDB, preserve inverter identity. Do not store only the combined value.

Recommended conceptual tags:

```text
inverter=1
inverter=2
system=combined
```

This enables future analysis of load sharing, PV production differences, temperature imbalance, and inverter-specific faults.

## Final production package

The planned production package will contain:

- two Modbus TCP hubs;
- complete per-inverter raw sensors;
- validated derived sensors;
- validated system aggregation;
- named fault sensors;
- availability monitoring;
- Energy Dashboard-ready counters;
- InfluxDB include/exclude guidance.

Do not promote the test package to production until the parallel-system validation matrix is complete.
