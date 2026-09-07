# Sol-Ark 15K Home Assistant Modbus

A local, read-only Home Assistant integration for Sol-Ark 15K hybrid inverters using native Modbus TCP through a Waveshare dual-channel RS485-to-PoE gateway.

This project is intended to replace a failed or unwanted SolarAssistant monitoring path while preserving local, direct access to inverter telemetry. The initial target is a pair of parallel Sol-Ark 15K inverters, with one isolated RS485 channel per inverter.

> **Project status:** active development / field validation. Monitoring first; no Modbus writes.

## What this project provides

- Native Home Assistant `modbus:` configuration for Sol-Ark 15K telemetry.
- Waveshare 2-CH RS485 TO POE ETH (B) setup guidance.
- Reuse of the RS485 side of a Sol-Ark/SolarAssistant CAN/RS485 splitter where applicable.
- A no-dependency Python Modbus TCP probe for commissioning.
- A working register reference derived from the public Sol-Ark Modbus RTU Protocol V1.4.
- Single-inverter commissioning before dual-inverter deployment.
- Dual-inverter design and aggregation guidance.
- Home Assistant dashboard examples.
- InfluxDB long-term retention design.
- UGREEN NAS deployment guidance for the production historian.
- Grafana dashboard design for multi-year historical analysis.
- Fault-word monitoring and future fault decoding.
- Troubleshooting and validation procedures.

## Target architecture

```text
Sol-Ark 15K #1
Battery/CAN port
      |
      v
Existing CAN/RS485 splitter
      |
      +---- CAN --------------------> Battery BMS
      |
      +---- RS485 ------------------> Waveshare CH1
                                        |
                                        | Modbus TCP
                                        v
                                  Home Assistant
                                        |
                                        +--> Recorder / HA statistics
                                        |
                                        +--> InfluxDB API :8086
                                                |
                                                v
                                           UGREEN NAS
                                      InfluxDB OSS 2.8.0
                                         bucket: solark
                                                |
                                                v
                                             Grafana

Sol-Ark 15K #2
Battery/CAN port
      |
      v
Existing CAN/RS485 splitter
      |
      +---- CAN --------------------> Battery BMS
      |
      +---- RS485 ------------------> Waveshare CH2
```

The two inverter RS485 links remain electrically independent. Each Waveshare channel is treated as a separate Modbus TCP gateway.

The production historian is hosted on the UGREEN NAS rather than on the Home Assistant system disk. Grafana may continue to run in Home Assistant while querying the NAS-hosted InfluxDB instance.

## Protocol baseline

The project currently uses the public **Sol-Ark Modbus RTU Protocol V1.4** as its primary register reference. For the 15K, the document specifies:

- read operations only;
- Modbus function code 03 for holding-register reads;
- 9600 baud;
- 8 data bits;
- no parity;
- 1 stop bit;
- fixed slave ID `0x01` for this map;
- signal ground connected between inverter and master;
- 120-ohm termination at the master side;
- CAN-based battery communications can coexist with this read protocol when the inverter is configured appropriately;
- RS485-based battery communications cannot be used simultaneously with this protocol.

The Parallel-screen **Modbus SN is not the slave ID for this map**. Each independently connected inverter is polled as slave ID 1.

## Important safety and support notice

This repository is an independent community project. It is **not affiliated with, endorsed by, or supported by Sol-Ark**.

The Sol-Ark V1.4 document states that Sol-Ark does not provide technical support for third-party Modbus devices or the Modbus map and that the map is intended for read operations. This repository therefore begins with a strict read-only design.

Do not add register writes unless the applicable Sol-Ark documentation explicitly supports them and the risks are understood.

## Hardware

### Recommended gateway — Waveshare 2-CH RS485 TO POE ETH (B)

[![Waveshare 2-CH RS485 TO POE ETH (B)](https://www.waveshare.com/wiki/Special:Redirect/file/2-CH%20RS485%20TO%20ETH%20%28B%29.jpg)](https://www.waveshare.com/product/iot-communication/wired-comm-converter/2-ch-rs485-to-eth-b.htm)

> **Use the PoE model:** select **2-CH RS485 TO POE ETH (B)**, not the non-PoE **2-CH RS485 TO ETH (B)** variant.

Why this gateway fits the project:

- two isolated RS485 channels that can operate independently;
- PoE-powered Ethernet on the PoE variant, IEEE 802.3af compliant;
- Modbus TCP ↔ Modbus RTU gateway support;
- web-based configuration;
- DIN-rail-capable industrial enclosure;
- one RS485 channel can be dedicated to each Sol-Ark 15K.

For a two-inverter installation:

```text
Waveshare CH1 -> Sol-Ark #1 RS485
Waveshare CH2 -> Sol-Ark #2 RS485
```

Official Waveshare sources:

- [Waveshare product page — 2-CH RS485 TO ETH (B) / 2-CH RS485 TO POE ETH (B)](https://www.waveshare.com/product/iot-communication/wired-comm-converter/2-ch-rs485-to-eth-b.htm)
- [Waveshare Wiki — 2-CH RS485 TO POE ETH (B)](https://www.waveshare.com/wiki/2-CH_RS485_TO_POE_ETH_(B))
- [Waveshare Wiki image source](https://www.waveshare.com/wiki/File:2-CH_RS485_TO_ETH_(B).jpg)

The official Waveshare page covers both the standard Ethernet and PoE variants. This project specifically targets the **PoE** version.

See [`docs/hardware.md`](docs/hardware.md), [`docs/wiring.md`](docs/wiring.md), and [`docs/waveshare-setup.md`](docs/waveshare-setup.md).

## Recommended commissioning sequence

Do not begin by connecting both inverters.

1. Confirm the battery is using CAN communications rather than RS485 battery communications.
2. Connect only Sol-Ark #1 to Waveshare channel 1.
3. Configure the Waveshare channel for Modbus TCP ↔ RTU, TCP port 502, and 9600/8/N/1 serial settings.
4. Verify TCP reachability.
5. Run the included Python probe.
6. Compare live values with the Sol-Ark display.
7. Enable the Home Assistant test package.
8. Validate signed values and temperature scaling.
9. Run for a stability period.
10. Repeat on Sol-Ark #2 / Waveshare channel 2.
11. Only then build combined dual-inverter sensors.

See [`docs/first-test.md`](docs/first-test.md).

## Repository layout

```text
.
├── README.md
├── LICENSE
├── NOTICE
├── THIRD_PARTY_NOTICES.md
├── docs/
│   ├── architecture.md
│   ├── hardware.md
│   ├── wiring.md
│   ├── waveshare-setup.md
│   ├── first-test.md
│   ├── home-assistant.md
│   ├── dual-inverter.md
│   ├── influxdb.md
│   ├── nas-influxdb.md
│   ├── grafana.md
│   └── troubleshooting.md
├── docker/
│   └── influxdb-compose.yml
├── homeassistant/
│   ├── packages/
│   │   └── solark15k_test_package.yaml
│   └── dashboards/
│       └── solark15k_test_dashboard.yaml
├── modbus/
│   └── solark15k_v1_4_register_map.csv
└── tools/
    └── solark_modbus_probe.py
```

## Long-term data plan

Home Assistant should not be asked to retain every high-frequency state change for many years in its normal Recorder database. The intended architecture is:

- Home Assistant Recorder for normal HA operation and short-term history;
- Home Assistant long-term statistics for native energy/statistical history;
- InfluxDB OSS 2.8.0 on the UGREEN NAS for high-resolution time-series retention;
- Grafana for advanced historical visualization and analysis.

The `solark` bucket is deliberately restricted to entities created by this integration and project-defined formulas derived from those entities. It is not a general Home Assistant historian.

The planned retention model keeps high-resolution data for a shorter period while retaining downsampled one-minute, fifteen-minute, hourly, and daily data for years.

The NAS container is pinned to `influxdb:2.8.0`. Do not treat changes to a generic Docker `latest` tag as an instruction to migrate this project. Any move to InfluxDB 3 should be deliberate and include data migration, Grafana query conversion, compatibility testing, and rollback planning.

See [`docs/influxdb.md`](docs/influxdb.md), [`docs/nas-influxdb.md`](docs/nas-influxdb.md), and [`docs/grafana.md`](docs/grafana.md).

## Current field-validation priorities

Before the project is considered production-ready, validate these against live 15K data:

- battery power sign convention;
- battery current sign convention;
- battery temperature encoding on current firmware;
- grid/load/battery values in a parallel two-inverter system;
- which measurements are per-inverter versus already system-wide;
- long-term energy counter word ordering;
- fault-word behavior during real events.

## Contributing

Issues and pull requests are welcome. For any proposed register change, include:

- inverter model;
- firmware version if known;
- register address;
- raw value;
- interpreted value;
- comparison source, such as the inverter display;
- whether the inverter is standalone or parallel.

Avoid submitting undocumented write-register functionality.

## License

Original code, configuration, and documentation in this repository are licensed under the **Apache License 2.0**. Third-party documentation, trademarks, and product names remain the property of their respective owners. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
