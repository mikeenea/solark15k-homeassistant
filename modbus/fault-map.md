# Sol-Ark V1.4 Fault Bit Reference

The public Sol-Ark Modbus RTU Protocol V1.4 defines fault information across registers 103-106 as four 16-bit words, providing a 64-bit fault bitmap.

This file is an implementation-oriented reference for the bits explicitly named in the public map.

## Word layout

```text
Register 103 -> bits 0-15
Register 104 -> bits 16-31
Register 105 -> bits 32-47
Register 106 -> bits 48-63
```

## Defined fault bits

| Global bit | Code | Name / meaning from V1.4 | Notes |
|---:|---|---|---|
| 7 | F08 | GFDI_Relay_Failure | |
| 12 | F13 | Grid_Mode_changed | Notification; not described as a fault |
| 13 | F14 | DC_OverCurr_Fault | |
| 14 | F15 | SW_AC_OverCurr_Fault | Often associated with excessive load / discharge limit |
| 15 | F16 | GFCI_Failure | Ground-fault related |
| 17 | F18 | HW_Ac_OverCurr_Fault | AC overload/short related |
| 19 | F20 | Tz_Dc_OverCurr_Fault | Excessive DC/battery current |
| 21 | F22 | Tz_EmergStop_Fault | V1.4 directs user to Sol-Ark |
| 22 | F23 | Tz_GFCI_OC_Fault | PV ground-fault related |
| 23 | F24 | DC_Insulation_ISO_Fault | Insulation/moisture related |
| 25 | F26 | BusUnbalance_Fault | L1/L2 imbalance or related conditions |
| 28 | F29 | Parallel_Fault | One or more parallel systems have an error |
| 32 | F33 | AC_OverCurr_Fault | |
| 33 | F34 | AC_Overload_Fault | |
| 40 | F41 | AC_WU_OverVolt_Fault | |
| 42 | F43 | AC_VW_OverVolt_Fault | |
| 44 | F45 | AC_UV_OverVolt_Fault | V1.4 describes grid under-voltage/disconnect behavior |
| 45 | F46 | Parallel_Aux_Fault | Parallel communications problem |
| 46 | F47 | AC_OverFreq_Fault | Grid over-frequency |
| 47 | F48 | AC_UnderFreq_Fault | Grid under-frequency |
| 54 | F55 | DC_VoltHigh_Fault | High PV/battery voltage condition |
| 55 | F56 | DC_VoltLow_Fault | Battery over-discharge/BMS shutdown condition |
| 57 | F58 | AC_U_GridCurr_High_Fault | |
| 60 | F61 | Button_Manual_OFF | |
| 61 | F62 | AC_B_InductCurr_High_Fault | |
| 62 | F63 | Arc_Fault | PV arc/connector or possible false alarm condition |
| 63 | F64 | Heatsink_HighTemp_Fault | Fan/ambient temperature related |

## Bit extraction

For a global bit number `b`:

```text
word_index = floor(b / 16)
bit_in_word = b % 16
register = 103 + word_index
mask = 1 << bit_in_word
```

Example: F46 is global bit 45.

```text
word_index = 45 // 16 = 2
register = 103 + 2 = 105
bit_in_word = 45 % 16 = 13
mask = 1 << 13 = 0x2000
```

A future Home Assistant production package can decode each documented bit into a named binary sensor.

## Commissioning recommendation

During early validation, retain the raw fault words in Home Assistant and InfluxDB even after named sensors are added. The raw values provide a complete record for future reinterpretation and debugging.

## Event capture

When any fault bit becomes active, future automation should snapshot:

```text
inverter identity
fault code(s)
time
PV power
load power
grid power
battery power
battery SOC
grid voltage L1/L2
grid frequency
inverter temperature
```

This will support historical fault forensics in InfluxDB/Grafana.

## Caution

This reference preserves the terminology and descriptions from the public V1.4 map where defined. It should not be treated as a replacement for Sol-Ark service documentation or electrical troubleshooting procedures.
