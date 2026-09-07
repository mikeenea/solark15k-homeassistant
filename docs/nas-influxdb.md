# UGREEN NAS InfluxDB Deployment

## Purpose

The production historian for this project runs on the UGREEN NAS rather than inside Home Assistant OS.

This separates long-term Sol-Ark history from the Home Assistant host and avoids making the Home Assistant system disk the primary home for multi-year time-series data.

Current field-verified architecture:

```text
Sol-Ark 15K #1/#2
        |
        v
Waveshare Modbus gateway
        |
        v
Home Assistant
        |
        | InfluxDB API :8086
        v
UGREEN NAS
InfluxDB OSS 2.8.0
bucket: solark
        |
        v
Grafana
```

The `solark` bucket is reserved for project-created Sol-Ark entities and formulas derived from those entities. It is not a general Home Assistant historian.

## Docker deployment

The UGREEN NAS deployment uses Docker/Projects with the image pinned to:

```text
influxdb:2.8.0
```

Do not replace the pinned tag with `latest` as part of routine maintenance. Any migration to InfluxDB 3 is a separate project decision because the current Grafana design uses Flux queries and the long-term historian requirements should be re-evaluated before changing database generations.

Reference compose file:

```text
docker/influxdb-compose.yml
```

The container persists:

```text
./data   -> /var/lib/influxdb2
./config -> /etc/influxdb2
```

The NAS project directory therefore contains the live database and configuration outside the disposable container layer.

## Initial InfluxDB setup

The current installation was initialized with:

```text
Organization: home
Bucket:       solark
Port:         8086
Retention:    unlimited during commissioning
```

Use a strong administrator password and do not store administrator credentials or API tokens in this repository.

## API tokens

Use separate least-privilege tokens:

### Home Assistant

Create a custom token such as:

```text
homeassistant-solark
```

Required permission:

```text
solark bucket: WRITE
```

Read permission is optional for the Home Assistant writer.

### Grafana

Create a separate custom token such as:

```text
grafana-solark-read
```

Required permission:

```text
solark bucket: READ
```

Do not give Grafana write permission unless a future feature specifically requires it.

## Home Assistant connection

Current Home Assistant releases migrate InfluxDB connection/authentication settings away from YAML into the InfluxDB integration configuration entry.

The live connection should point to the NAS:

```text
URL:          http://<UGREEN-NAS-IP>:8086
Bucket:       solark
Organization: the NAS InfluxDB organization configured for this installation
Token:        homeassistant-solark token
```

The project intentionally keeps the entity-selection filter in YAML.

Example:

```yaml
influxdb:
  include:
    entity_globs:
      - sensor.sol_ark_test_*
      - binary_sensor.sol_ark_test_*
      - sensor.sol_ark_1_*
      - binary_sensor.sol_ark_1_*
      - sensor.sol_ark_2_*
      - binary_sensor.sol_ark_2_*
      - sensor.sol_ark_system_*
      - binary_sensor.sol_ark_system_*
```

Connection/authentication keys such as `host`, `port`, `token`, `organization`, and `bucket` should not be duplicated in YAML after the UI config entry is working.

## Grafana connection

Grafana may continue to run in Home Assistant while reading InfluxDB from the NAS.

Use a Flux data source configured conceptually as:

```text
URL:            http://<UGREEN-NAS-IP>:8086
Query language: Flux
Organization:   home
Default bucket: solark
Token:          grafana-solark-read
```

A simple connection test in Grafana Explore is:

```flux
buckets()
```

The result should include:

```text
solark
```

A bucket-read test is:

```flux
from(bucket: "solark")
  |> range(start: -24h)
  |> limit(n: 10)
```

During pre-hardware staging, zero series is expected because the Sol-Ark entities remain `unknown` until the Waveshare gateway is installed and valid Modbus values are received. Unauthorized, bucket-not-found, or connection errors are not expected.

## Current field status

As of September 2026:

- UGREEN Docker project `solark-influxdb` is running;
- InfluxDB OSS 2.8.0 is running from the pinned Docker image;
- the `solark` bucket exists on the NAS;
- Home Assistant has been reconfigured to target the NAS InfluxDB instance;
- Grafana has been reconfigured to target the NAS InfluxDB instance;
- Grafana connection testing succeeds and sees one bucket;
- the bucket is intentionally empty until live Sol-Ark Modbus values exist;
- the older Home Assistant-hosted InfluxDB instance is no longer the intended production historian.

## Backup and storage notes

RAID protects against some disk failures but is not a substitute for backup.

Back up the NAS InfluxDB project data and configuration separately from the primary NAS volume when practical.

Recommended project data to protect:

```text
Docker project/compose definition
InfluxDB data directory
InfluxDB configuration directory
InfluxDB backup exports when implemented
Grafana dashboard JSON
Home Assistant configuration
```

Do not store API tokens in GitHub.

## Upgrade policy

Keep the production historian pinned to InfluxDB OSS 2.8.0 during Sol-Ark commissioning and initial data collection.

Do not treat a future change in the Docker `latest` tag as an instruction to migrate this project. A move to InfluxDB 3 should be deliberate and should include:

- historian retention requirements;
- migration/backup procedure;
- Grafana query-language conversion;
- compatibility testing with Home Assistant;
- rollback planning;
- preservation of existing Sol-Ark history.
