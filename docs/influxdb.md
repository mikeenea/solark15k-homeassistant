# InfluxDB Long-Term Historian

## Objective

Use InfluxDB as the high-resolution, multi-year historian for **only the entities created by this Sol-Ark integration and formulas derived from those entities**, while leaving Home Assistant Recorder in place for normal Home Assistant operation.

This project intentionally does **not** use InfluxDB as a general Home Assistant historian. Existing JK, SOK, iBMS, YamBMS, weather, lighting, networking, automation, system, and other unrelated Home Assistant entities are outside the scope of this database unless they are later explicitly incorporated into a Sol-Ark-derived formula by design.

The design goal is to preserve enough detail for Sol-Ark troubleshooting and performance analysis without storing unrelated Home Assistant data or every 10-second value forever.

## Current Home Assistant OS installation note

As of September 2026, do **not** use the older `danieloldberg/addon-influxdbv2` Home Assistant app for this project. On an amd64 Home Assistant OS host, version `v0.0.4` was observed failing during its local Docker build because the Debian Bullseye security repository returned `404 Not Found` for required packages such as `libc-dev-bin` and `linux-libc-dev`. This is an app build/dependency problem, not a Sol-Ark, Home Assistant entity, disk-space, or Modbus problem.

The currently recommended HAOS repository for this project is:

```text
https://github.com/naked-head/homeassistant-addons
```

That repository provides **InfluxDB OSS 2.8.0** as a Home Assistant Supervisor app. Add it under:

```text
Settings -> Apps -> App Store -> three-dot menu -> Repositories
```

Then install the app named **InfluxDB** from that repository.

Grafana remains available from the Home Assistant Community Apps repository:

```text
https://github.com/hassio-addons/repository
```

This recommendation should be revisited periodically because third-party Home Assistant app maintenance can change.

## Data-flow role

```text
Sol-Ark -> Waveshare -> Home Assistant -> InfluxDB -> Grafana
                               |
                               +-> Recorder / HA long-term statistics
```

InfluxDB complements Home Assistant; it does not replace Recorder.

## Strict data boundary

The `solark` bucket is reserved for this project.

Allowed data sources are:

1. direct Sol-Ark Modbus entities created by this repository;
2. Home Assistant template/formula entities created by this repository from those Sol-Ark entities;
3. project-created communications, availability, fault, and diagnostic entities directly associated with the Sol-Ark integration.

The following are excluded by design:

- JK BMS entities;
- SOK BMS entities;
- iBMS entities;
- YamBMS entities;
- ESPHome entities unrelated to this integration;
- lights, switches, weather, device trackers, updates, automations, system metrics, and other general Home Assistant entities;
- any third-party sensor that is not explicitly part of a project-defined Sol-Ark formula.

Grafana dashboards for this project must query only the project-created Sol-Ark entity namespace and derived project formulas.

## Entity namespace and InfluxDB filtering

During first-test commissioning, the current test package creates Home Assistant entity names based on the `Sol-Ark Test ...` names. These normally resolve to the `sensor.sol_ark_test_*` and `binary_sensor.sol_ark_test_*` namespaces.

The production implementation will use dedicated namespaces for inverter #1, inverter #2, and system-level formulas. The intended logical namespaces are:

```text
sensor.solark_1_*
sensor.solark_2_*
sensor.solark_system_*
binary_sensor.solark_1_*
binary_sensor.solark_2_*
binary_sensor.solark_system_*
```

Until production naming is finalized, an InfluxDB include-only filter should cover only the current test namespace plus those future production namespaces:

```yaml
influxdb:
  include:
    entity_globs:
      - sensor.sol_ark_test_*
      - binary_sensor.sol_ark_test_*
      - sensor.solark_1_*
      - binary_sensor.solark_1_*
      - sensor.solark_2_*
      - binary_sensor.solark_2_*
      - sensor.solark_system_*
      - binary_sensor.solark_system_*
```

Do **not** add JK, SOK, iBMS, YamBMS, or general Home Assistant globs to this project database.

If the production entity namespace changes, update both the Home Assistant InfluxDB include filter and this document together.

## Why a separate historian

A pair of 15K inverters can expose dozens of telemetry values. Sampling 60-100 values every 10 seconds creates a large volume of state changes over multiple years.

A time-series database is better suited for:

- high-resolution history;
- downsampling;
- retention policies;
- range queries spanning years;
- min/mean/max aggregation;
- season-over-season comparisons;
- fault-event forensic analysis.

## Recommended retention tiers

The exact implementation depends on the InfluxDB version, but the logical retention model should be:

| Tier | Resolution | Suggested retention | Purpose |
|---|---|---:|---|
| Raw | 10 s / native HA changes | 180 days | forensic troubleshooting |
| Detailed | 1 minute | 5 years | long-term detailed analysis |
| Trend | 15 minutes | indefinite | multi-year trend analysis |
| Summary | 1 hour / 1 day | indefinite | reports and year-over-year comparison |

This is a starting design, not a hard requirement.

## Priority signals for extended full-resolution retention

If storage capacity permits, retain these core power-flow sensors at higher resolution for longer:

```text
system PV power
system load power
system grid power
system battery power
battery SOC
inverter #1 total output
inverter #2 total output
generator power
```

These few signals explain most operational events.

## Per-inverter detail

Preserve per-inverter measurements rather than exporting only combined templates. Important examples:

```text
PV1/2/3 power by inverter
inverter L1/L2 power by inverter
heat-sink temperature by inverter
fault words by inverter
battery power/current as reported by each inverter
load/grid registers by inverter until parallel semantics are validated
```

This allows future diagnosis of inverter imbalance and failures without relying on unrelated BMS telemetry.

## Recommended measurement model

There are two viable approaches:

### Home Assistant default entity-oriented export

Use the standard Home Assistant InfluxDB integration and retain entity IDs/tags. This is easiest and preserves Home Assistant naming, provided the include-only filter is enforced.

### Curated schema

For advanced installations, normalize measurements conceptually as:

```text
measurement: solark

tags:
  site=home
  inverter=1|2|system
  source=modbus|formula

fields:
  pv1_power
  pv2_power
  pv3_power
  pv_total_power
  load_power
  grid_power
  battery_power
  battery_voltage
  battery_current
  battery_soc
  heat_sink_temperature
```

The initial repository will favor the standard HA integration, then add curated queries where useful.

## Raw diagnostic registers

During early field validation, retain raw values for unusual Sol-Ark registers:

```text
battery temperature raw
battery power raw
battery current raw
fault words 103-106
grid relay raw
generator relay raw
total grid import low word 78
total grid import high word 80
```

Once behavior is well established, some raw values may be excluded from long-term storage.

## Downsampling strategy

For numeric measurements such as power and temperature, downsample using:

```text
minimum
mean
maximum
last
```

A one-minute bucket containing min/mean/max preserves spikes better than keeping only a simple average.

For counters such as cumulative energy, use the appropriate last/max/change logic rather than averaging the counter itself.

For boolean or enum states, preserve transitions or calculate duration within each state.

## Daily summary dataset

Create or derive daily values such as:

```text
PV energy produced
load energy consumed
grid import energy
grid export energy
battery charge energy
battery discharge energy
peak PV power
peak load power
peak grid import
peak grid export
minimum battery SOC
maximum battery SOC
minimum/maximum grid voltage by leg
generator runtime
generator energy
grid outage duration
fault count by code
```

These summaries are ideal for indefinite retention.

## Multi-year analysis use cases

The historian should support questions such as:

- How much PV did September 2028 produce compared with September 2027?
- Is winter battery throughput increasing year over year?
- Are inverter heat-sink temperatures trending upward?
- Is one MPPT/string consistently underperforming?
- How often has the grid failed in the past five years?
- How long did each outage last?
- Did a fault occur during high load, low SOC, or abnormal grid voltage?
- Is load sharing between the two inverters balanced?

## Backup strategy

Treat the historian as important operational data.

Suggested policy:

```text
Daily backup: retain 14 days
Weekly backup: retain 8 weeks
Monthly backup: retain 24 months or longer
```

Store backups separately from the primary Home Assistant system disk when practical.

## Rebuild philosophy

The Home Assistant YAML and Grafana dashboards belong in GitHub and can be recreated. The time-series data itself cannot be recreated after loss unless another source retained it.

Therefore prioritize backups of:

1. InfluxDB data;
2. InfluxDB configuration/retention tasks;
3. Grafana provisioning/dashboards;
4. Home Assistant configuration.

## Returning historical values to Home Assistant

Selected InfluxDB query results can be exposed back to Home Assistant as project-created formula/history sensors, for example:

```text
sensor.solark_system_pv_yesterday
sensor.solark_system_pv_month_to_date
sensor.solark_system_pv_last_month
sensor.solark_system_pv_year_to_date
sensor.solark_system_peak_load_today
sensor.solark_system_min_soc_30_days
sensor.solark_system_grid_import_month
sensor.solark_system_grid_export_month
```

This provides simple historical context inside normal Home Assistant dashboards while Grafana remains the advanced analysis interface.

## Implementation phases

### Phase 1

Verify Sol-Ark Modbus entities.

### Phase 2

Export only verified project-created Sol-Ark entities and formulas to InfluxDB at native update rate.

### Phase 3

Build Grafana live/24-hour dashboards using only those entities.

### Phase 4

Add retention/downsampling.

### Phase 5

Add daily/monthly/yearly comparison dashboards and HA historical query sensors.

Do not optimize retention until the live entity set and naming conventions have stabilized.
