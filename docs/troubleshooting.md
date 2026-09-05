# Troubleshooting

## Troubleshooting philosophy

Troubleshoot the system in layers. Do not change RS485 wiring, Modbus settings, Home Assistant YAML, and network settings simultaneously.

Use this order:

```text
1. Ethernet / IP
2. TCP port 502
3. Waveshare protocol configuration
4. RS485 wiring and ground
5. RS485 termination
6. Sol-Ark protocol prerequisites
7. Raw Modbus probe
8. Home Assistant configuration
9. Register interpretation
10. Parallel-inverter aggregation
```

## Symptom: Waveshare IP cannot be reached

Check:

- PoE/power LED status;
- Ethernet link LEDs;
- switch port status;
- DHCP lease or static IP;
- VLAN assignment;
- local firewall/routing;
- duplicate IP address.

Do not troubleshoot Sol-Ark wiring until the gateway is reachable.

## Symptom: IP reachable but TCP 502 fails

Run:

```powershell
Test-NetConnection <waveshare-ip> -Port 502
```

If false:

- verify Modbus TCP ↔ RTU mode;
- verify TCP Server mode;
- verify port 502;
- save/reboot the Waveshare channel;
- check firewall/VLAN policy.

## Symptom: TCP 502 works but Modbus probe times out

Likely causes:

- RS485 A/B reversed or disconnected;
- GND not connected;
- wrong serial settings;
- wrong gateway conversion mode;
- incorrect termination;
- Sol-Ark BMS Lithium Batt mode not `00`;
- battery using RS485 instead of CAN;
- wrong physical splitter jack/path;
- damaged cable.

Verify 9600/8/N/1 and slave ID 1.

## Symptom: Modbus exception response

The Python probe reports Modbus exceptions separately from network timeouts.

Possible causes:

- invalid register range;
- gateway not transparently passing the correct function;
- unsupported register on current firmware/model;
- incorrect unit/slave handling.

Test a small known-good range such as registers 183-184 after basic connectivity is proven.

## Symptom: all values are zero

Possible causes:

- wrong register addresses;
- gateway cache/storage mode returning zeros;
- unsupported range;
- Modbus request reaching the wrong serial target;
- inverter operating state where some specific values are legitimately zero.

Check battery voltage and grid voltage first; they should normally provide obvious non-zero validation values on an operating system.

## Symptom: battery voltage is implausible

Register 183 uses 0.01 V scaling in the V1.4 map.

Example raw value:

```text
5200 -> 52.00 V
```

If the raw value itself is plausible but HA is not, inspect scaling. If raw data is implausible, investigate register addressing or protocol alignment.

## Symptom: temperature is around 100 C too high/low

The V1.4 map documents an offset encoding for battery temperature 182 and heat-sink temperature 91:

```text
C = raw * 0.1 - 100
```

Current firmware should be validated. Keep the raw value before changing the formula.

## Symptom: grid import/export direction is reversed

Register 169 is documented by V1.4 as:

```text
> 0 = BUY / import
< 0 = SELL / export
```

If the live system appears opposite, capture:

- register 167;
- register 168;
- register 169;
- CT1/CT2/total registers 170-172;
- inverter display;
- actual site operating condition.

Do not simply reverse the sign without documenting the evidence.

## Symptom: battery charge/discharge direction is reversed

Registers 190 and 191 are signed in the map, but the map does not clearly define charge versus discharge sign.

This is a field-validation item. Capture raw values while clearly charging and clearly discharging, then document the result.

## Symptom: Home Assistant reports unavailable but Python probe works

If the standalone probe works, the physical/network path is probably sound.

Check HA:

- correct host IP;
- port 502;
- `slave: 1`;
- `input_type: holding`;
- valid `data_type`;
- YAML indentation;
- duplicate Modbus hub names;
- duplicate `unique_id` values;
- Home Assistant logs for `modbus` errors;
- scan interval and timeout.

## Symptom: HA works initially then becomes intermittent

Investigate:

- excessive polling rate;
- two Modbus masters polling the same RS485 channel;
- Waveshare storage/autopolling left enabled;
- poor termination;
- missing ground;
- noise on the serial cable;
- network packet loss;
- duplicate IP address;
- power instability at the gateway.

Increase scan intervals during diagnosis.

## Symptom: one Waveshare channel works and the other does not

Use substitution testing:

1. keep the known-good inverter/cable unchanged;
2. move it to the suspect Waveshare channel;
3. configure the suspect channel identically except IP;
4. run the probe.

This separates inverter/cable issues from gateway-channel issues.

Do not swap multiple variables at once.

## Symptom: second inverter shows identical values to first

Possible explanations:

- both HA hubs accidentally point to the same Waveshare IP;
- both channels are configured to the same network endpoint;
- parallel firmware exposes duplicated system-level values for those registers;
- entity naming/templates are referencing the wrong sensors.

Compare raw probe output directly against each channel IP before changing aggregation logic.

## Symptom: combined system value is roughly double the inverter display

Likely cause: a system-wide register was duplicated by both parallel inverters and then summed in HA.

Remove the sum and classify the register using the procedure in [`dual-inverter.md`](dual-inverter.md).

## Symptom: combined system value is roughly half the expected total

Likely cause: a per-inverter value is being taken only from one inverter.

Verify both sources and whether they should be added.

## Symptom: lifetime energy values are extremely large

Check 32-bit word ordering.

The map identifies low and high words. Home Assistant may require a word swap depending on how `uint32` is decoded.

Special warning: total grid buy uses low word 78 and high word 80 with grid frequency at register 79. It must be reconstructed manually.

## Fault registers

Registers 103-106 contain a 64-bit fault bitmap. During initial commissioning, retain the four raw words.

If a fault appears:

1. record all four words in hex;
2. record time and inverter identity;
3. capture PV/load/grid/battery conditions;
4. decode the relevant bit using the V1.4 fault table;
5. do not clear or write inverter state through Modbus.

## Data-quality checklist

A healthy connection should usually satisfy:

- grid L1/L2 voltages plausible;
- battery voltage plausible;
- SOC 0-100%;
- grid/load/inverter frequency near expected system frequency;
- PV power consistent with daylight;
- no unexplained register freezes;
- update timestamps progress continuously;
- no large impossible jumps caused by signed/unsigned decoding.

## Information to include in a GitHub issue

```text
Inverter model:
Firmware:
Standalone or parallel:
Master/slave parallel role:
Waveshare model:
Channel:
Gateway IP:
Serial settings:
Termination:
Battery communications: CAN/RS485
Register(s):
Raw value(s):
Expected value:
Observed value:
Python probe output:
Home Assistant log excerpt:
What changed before failure:
```

Include enough data to reproduce the problem without posting passwords, private network credentials, or API tokens.
