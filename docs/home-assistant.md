# Home Assistant Native Modbus

## Goal

Home Assistant communicates directly with each Sol-Ark 15K through the Waveshare Modbus TCP gateway. No SolarAssistant, MQTT bridge, or custom HACS integration is required for the primary data path.

## Connection model

For the reference two-inverter installation:

```text
solark_1 -> Waveshare CH1 IP:502 -> slave 1
solark_2 -> Waveshare CH2 IP:502 -> slave 1
```

Each Waveshare channel is a separate TCP endpoint. The public Sol-Ark V1.4 map states that slave ID 1 is fixed for this protocol.

## Recommended package approach

Use Home Assistant packages so the Modbus hub definitions, raw sensors, template sensors, and binary sensors can live together.

Example `configuration.yaml` integration:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

If a `homeassistant:` section already exists, merge the `packages:` line into it rather than creating a duplicate top-level key.

## Initial single-inverter hub

```yaml
modbus:
  - name: solark_test
    type: tcp
    host: 192.168.1.241
    port: 502
    timeout: 5
    delay: 1
    message_wait_milliseconds: 100
```

The project test package then defines sensors beneath that hub.

## Polling strategy

Initial recommendations:

| Data class | Suggested interval |
|---|---:|
| Live power/current/voltage | 10 s |
| Fault words | 10 s |
| Relay state | 10 s |
| Temperature | 10-30 s |
| Daily energy | 60 s |
| Lifetime energy | 60 s |
| Static/configuration values | 60 s or longer |

The first objective is reliable telemetry, not maximum sample rate.

## Core live register groups

### PV

```text
109 PV1 voltage
110 PV1 current
111 PV2 voltage
112 PV2 current
113 PV3 voltage
114 PV3 current
186 PV1 power
187 PV2 power
188 PV3 power (15K)
```

### Grid and AC

```text
150 Grid L1-N voltage
151 Grid L2-N voltage
152 Grid L1-L2 voltage
160 Grid L1 current
161 Grid L2 current
167 Grid L1 power
168 Grid L2 power
169 Grid total power
```

The V1.4 map defines register 169 as positive for grid buy/import and negative for grid sell/export.

### CT / limiter

```text
162 External limiter current L1
163 External limiter current L2
170 CT1 power
171 CT2 power
172 External CT total power
```

### Inverter output

```text
154 Inverter L1-N voltage
155 Inverter L2-N voltage
156 Inverter L1-L2 voltage
164 Inverter L1 current
165 Inverter L2 current
173 Inverter L1 power
174 Inverter L2 power
175 Inverter total power
193 Inverter output frequency
```

### Load

```text
157 Load L1 voltage
158 Load L2 voltage
176 Load L1 power
177 Load L2 power
178 Load total power
179 Load L1 current
180 Load L2 current
192 Load frequency
```

### Battery

```text
107 Corrected battery capacity
182 Battery temperature
183 Battery voltage
184 Battery SOC
190 Battery output power
191 Battery output current
```

### Generator / AC-coupled port

```text
166 Generator or AC-coupled power
181 Generator port L1-L2 voltage
195 Generator relay status
196 Generator frequency
```

### Faults

```text
103 Fault word 1
104 Fault word 2
105 Fault word 3
106 Fault word 4
```

These four 16-bit registers form a 64-bit fault bitmap.

## Derived PV total

The 15K exposes three PV input power registers. A basic per-inverter total is:

```yaml
template:
  - sensor:
      - name: "Sol-Ark 1 Total PV Power"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: >
          {{ states('sensor.sol_ark_1_pv1_power') | float(0)
           + states('sensor.sol_ark_1_pv2_power') | float(0)
           + states('sensor.sol_ark_1_pv3_power') | float(0) }}
```

## Grid import/export split

Because register 169 uses positive=buy and negative=sell, create separate non-negative sensors:

```yaml
      - name: "Sol-Ark 1 Grid Import Power"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: >
          {% set p = states('sensor.sol_ark_1_grid_total_power') | float(0) %}
          {{ [p, 0] | max }}

      - name: "Sol-Ark 1 Grid Export Power"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: >
          {% set p = states('sensor.sol_ark_1_grid_total_power') | float(0) %}
          {{ [-p, 0] | max }}
```

## Battery charge/discharge split

Do **not** hard-code battery charge/discharge direction until register 190 sign convention is verified against a live inverter.

Once verified, create separate non-negative charge and discharge sensors using the same pattern as grid import/export.

## Energy counters

The project exposes both daily and lifetime values where practical.

Important counters include:

```text
70 Day battery charge
71 Day battery discharge
72/73 Total battery charge
74/75 Total battery discharge
76 Day grid buy
77 Day grid sell
78/80 Total grid buy (non-contiguous)
81/82 Total grid sell
84 Day load
85/86 Total load
96/97 Total PV
108 Daily PV
```

### Special case: total grid buy

Register 79 is grid frequency and sits between the low word at 78 and high word at 80. Therefore, total grid buy cannot be read as an ordinary contiguous `uint32` starting at 78.

Read 78 and 80 separately and reconstruct:

```text
value = ((high * 65536) + low) * 0.1 kWh
```

## Temperature scaling

The V1.4 map documents battery temperature register 182 with a +1000 raw offset and 0.1 C units:

```text
raw 1200 -> 20.0 C
```

Initial HA conversion:

```text
C = raw * 0.1 - 100
```

Register 91 heat-sink temperature uses the same offset style. Validate current firmware behavior before treating these as final.

## State classes

Use Home Assistant state classes carefully:

- instantaneous power/voltage/current/temperature -> `measurement`;
- monotonically increasing lifetime energy -> `total_increasing`;
- daily reset counters -> generally `measurement` unless a specific HA use case requires different handling.

This matters for long-term statistics and Energy Dashboard compatibility.

## Naming convention

Recommended entity naming:

```text
sensor.sol_ark_1_battery_voltage
sensor.sol_ark_1_battery_soc
sensor.sol_ark_1_pv1_power
sensor.sol_ark_1_grid_total_power
sensor.sol_ark_1_load_total_power

sensor.sol_ark_2_battery_voltage
...
```

System-level derived sensors should use a clear prefix such as:

```text
sensor.sol_ark_system_pv_power
sensor.sol_ark_system_grid_import_power
sensor.sol_ark_system_grid_export_power
sensor.sol_ark_system_load_power
```

Do not create system-level sums until parallel behavior has been validated.

## Recorder and database role

Home Assistant Recorder remains enabled for normal operation. Long-term high-resolution retention should be exported to InfluxDB rather than attempting to keep every 10-second state in Recorder for many years.

See [`influxdb.md`](influxdb.md) and [`grafana.md`](grafana.md).
