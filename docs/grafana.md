# Grafana Dashboard Plan

## Objective

Grafana is the primary advanced historical visualization layer for the Sol-Ark data stored in InfluxDB.

Home Assistant remains the operational interface; Grafana provides deeper time-series analysis, comparison, and troubleshooting.

## Dashboard set

The project plans several focused dashboards rather than one extremely dense page.

## 1. System Overview

Primary variables:

```text
Total PV power
Total load power
Grid import/export power
Battery charge/discharge power
Battery SOC
Generator power
Inverter #1 output
Inverter #2 output
```

Recommended panels:

- current power-flow stat cards;
- 24-hour PV/load/grid/battery overlay;
- battery SOC timeline;
- daily energy totals;
- inverter output comparison;
- active fault/communications status.

## 2. Dual-Inverter Balance

Purpose: identify unequal loading or temperature behavior.

Panels:

```text
Inverter #1 vs #2 total output
Inverter #1 vs #2 L1 power
Inverter #1 vs #2 L2 power
Inverter #1 vs #2 heat-sink temperature
PV production by inverter
Fault occurrence by inverter
```

Useful derived metrics:

```text
output difference W
output difference %
L1/L2 imbalance
heat-sink temperature difference
```

## 3. PV / MPPT Performance

Display all six MPPT channels separately for the two-inverter system:

```text
Sol-Ark #1 PV1/PV2/PV3
Sol-Ark #2 PV1/PV2/PV3
```

Recommended views:

- power by MPPT;
- voltage by MPPT;
- current by MPPT;
- daily energy by inverter;
- system PV total;
- normalized comparison between strings where array geometry supports comparison.

Long-term uses:

- detect shading changes;
- identify underperforming strings;
- identify failed connectors or input issues;
- compare seasonal performance;
- monitor gradual degradation.

## 4. Battery Dashboard

Panels:

```text
Battery SOC
Battery voltage
Battery power
Battery current
Battery temperature
Daily charge energy
Daily discharge energy
Minimum SOC by day
Maximum charge/discharge power
```

Future derived values:

- estimated equivalent full cycles;
- charge/discharge throughput;
- time spent below selected SOC thresholds;
- overnight discharge profile.

Battery sign convention must be field-validated before charge/discharge panels are finalized.

## 5. Grid Dashboard

Panels:

```text
Grid L1 voltage
Grid L2 voltage
Grid L1-L2 voltage
Grid frequency
Grid import power
Grid export power
CT1 / CT2 power
Daily import/export energy
Monthly import/export energy
```

Event analysis:

- voltage excursions;
- frequency excursions;
- grid disconnects;
- outage duration;
- import/export peaks.

## 6. Generator / AC-Coupled Dashboard

Panels:

```text
Generator/AC-coupled power register 166
Generator port voltage
Generator frequency
Generator relay state
Generator runtime derived from power/relay state
Generator energy if a reliable counter can be derived
```

The V1.4 map documents register 166 as positive when the GEN port acts as an output/load and negative when it receives AC input.

## 7. Fault and Event Dashboard

Store and visualize:

```text
Fault words 103-106
Decoded fault codes
Start time
End time
Duration
Inverter identity
PV at event
Load at event
Battery SOC at event
Battery power at event
Grid voltage/frequency at event
```

This turns a transient inverter fault into a reconstructable operating event.

## 8. Long-Term Energy Dashboard

Time ranges:

- current month;
- previous month;
- year to date;
- previous year;
- rolling 12 months;
- custom multi-year range.

Panels:

```text
PV energy by month
Load energy by month
Grid import by month
Grid export by month
Battery charge/discharge energy by month
Generator runtime by month
Peak load by month
Minimum SOC by month
```

## 9. Year-over-Year Dashboard

Purpose: compare equivalent calendar periods.

Examples:

```text
Jan-Dec 2027 vs Jan-Dec 2028
September 2027 vs September 2028
Summer quarter comparison
Winter quarter comparison
```

Use normalized daily or monthly aggregates rather than plotting millions of raw samples.

## Dashboard time resolution

Suggested query resolution:

| Display range | Preferred resolution |
|---|---|
| Last 6 hours | raw / 10 s |
| Last 24-48 hours | raw or 1 minute |
| 7-30 days | 1-15 minute |
| 1 year | hourly/daily |
| Multiple years | daily/monthly |

## Alerting philosophy

Home Assistant should remain the primary automation/notification engine for critical events. Grafana alerts may be added later for data-quality or historical conditions, but avoid duplicating every HA alert.

Possible Grafana-specific alerts:

- no data from an inverter for a defined interval;
- sustained imbalance between inverter outputs;
- abnormal heat-sink temperature differential;
- long-term MPPT underperformance;
- database ingestion gap.

## Dashboard-as-code

Whenever practical, export Grafana dashboards as JSON and store them under:

```text
grafana/dashboards/
```

This allows dashboard restoration, review, and version control.

Do not store credentials, API tokens, or datasource secrets in GitHub.

## Planned repository additions

Future files will include:

```text
grafana/dashboards/system-overview.json
grafana/dashboards/dual-inverter.json
grafana/dashboards/pv-mppt.json
grafana/dashboards/battery.json
grafana/dashboards/grid.json
grafana/dashboards/fault-events.json
```

These will be added after live entity names and InfluxDB field/tag conventions are validated.
