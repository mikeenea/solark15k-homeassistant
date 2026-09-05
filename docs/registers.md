# Register Mapping Notes

## Source basis

The initial mapping is derived from the public **Sol-Ark Modbus RTU Protocol V1.4**, which explicitly includes the Sol-Ark 15K.

The repository does not redistribute the source PDF. Instead, it maintains an implementation-oriented CSV under:

```text
modbus/solark15k_v1_4_register_map.csv
```

## Protocol characteristics

The V1.4 document defines:

```text
Function code: 0x03 / Read Multiple Holding Registers
Baud: 9600
Data bits: 8
Parity: None
Stop bits: 1
Slave ID: 0x01
```

The Parallel-screen Modbus SN is separate from this map's fixed slave ID.

## Read-only policy

The project does not define write registers. The first production goal is comprehensive monitoring and historical analysis.

## Core ranges

The project currently focuses on several register groups:

### 60-114

Includes:

- active-energy counters;
- daily/lifetime battery energy;
- grid buy/sell energy;
- load energy;
- temperatures;
- total PV energy;
- fault words;
- battery capacity;
- PV voltages/currents.

### 150-196

Includes:

- grid voltages/currents/powers;
- external CT values;
- inverter output voltages/currents/powers;
- load voltages/currents/powers;
- generator/AC-coupled values;
- battery voltage/SOC/power/current;
- PV input power;
- frequencies;
- relay states.

## Data-type rules

### Unsigned 16-bit

Use `uint16` for measurements whose map ranges are non-negative, such as:

```text
PV voltage/current
battery voltage
battery SOC
frequency
energy daily counters
```

### Signed 16-bit

Use `int16` where V1.4 explicitly marks signed values, including:

```text
grid current
inverter current
grid power
CT power
inverter power
load power
battery power
battery current
generator/AC-coupled power
```

A raw unsigned word above 32767 must therefore be interpreted using two's-complement signed conversion for those registers.

## Scaling rules

Examples:

```text
Grid voltage: raw * 0.1 V
Grid current: raw_signed * 0.01 A
Grid frequency: raw * 0.01 Hz
Battery voltage: raw * 0.01 V
Battery SOC: raw %
PV power: raw W
Energy counters: raw * 0.1 kWh
```

## Temperature offset

V1.4 documents battery temperature register 182 as an offset value where:

```text
raw 1200 = 20.0 C
```

Initial formula:

```text
C = raw * 0.1 - 100
```

The heat-sink temperature register 91 uses the same style of offset in the public map.

Because firmware behavior can change, retain the raw value during field validation.

## 32-bit low/high words

Many lifetime counters use separate low and high 16-bit words.

General reconstruction:

```text
value32 = (high << 16) | low
engineering_value = value32 * scale
```

Examples:

```text
72 low + 73 high -> total battery charge
74 low + 75 high -> total battery discharge
81 low + 82 high -> total grid sell
85 low + 86 high -> total load
96 low + 97 high -> total PV
```

## Non-contiguous total grid buy

Total grid buy is a special case:

```text
78 = low word
79 = grid frequency
80 = high word
```

Therefore the value must be reconstructed from 78 and 80 explicitly.

Do not use a contiguous `uint32` starting at 78.

## Sign conventions

### Grid total power 169

V1.4 explicitly states:

```text
positive -> BUY/import
negative -> SELL/export
```

This is safe to use for initial HA grid import/export template sensors.

### Generator / AC-coupled power 166

V1.4 describes:

```text
positive -> GEN port acting as load/output
negative -> AC power entering the port
```

### Battery power/current 190/191

The map marks these as signed but does not clearly define charge versus discharge sign. The repository treats this as a required field-validation item.

## Relay states

### Grid relay 194

```text
1 -> Open / disconnected
2 -> Closed
```

### Generator relay 195

The V1.4 map describes the low four bits/state values as:

```text
0 -> Open
1 -> Closed
2 -> No Connection
3 -> Closed when Generator is on
```

## Fault words

Registers 103-106 form a 64-bit bitmap. See:

```text
modbus/fault-map.md
```

The test package initially exposes raw words and a generic `Any Fault` binary sensor. Named fault sensors will be added after live validation.

## Parallel-inverter caution

Register correctness is not the same as aggregation correctness.

Even if register 178 correctly reports `Load side Total power`, a parallel pair may expose that quantity as per-inverter or system-wide depending on firmware behavior.

Therefore this project separates:

1. register decoding; from
2. multi-inverter aggregation semantics.

See `docs/dual-inverter.md`.

## Change-control rule

Any change to a register mapping should document:

- model;
- firmware;
- raw value;
- old interpretation;
- new interpretation;
- comparison evidence;
- whether the system is standalone or parallel.

This keeps the mapping evidence-based and reviewable.
