# Hardware Guide

## Required hardware

For the reference two-inverter installation:

- 2 × Sol-Ark 15K hybrid inverters.
- 1 × Waveshare **2-CH RS485 TO POE ETH (B)** gateway.
- Existing Sol-Ark/SolarAssistant CAN/RS485 splitters, if already installed and proven.
- 2 × passive RJ45 patch leads or RJ45-to-terminal leads for the splitter RS485 outputs.
- 1 × Ethernet connection from the Waveshare to the LAN.
- IEEE 802.3af-compatible PoE source if powering the Waveshare by PoE.
- Multimeter with continuity and resistance modes.
- Optional 120-ohm RS485 termination resistor if the Waveshare channel does not already provide the required master-side termination.

## Why the two-channel Waveshare

The two-channel gateway is preferred because each Sol-Ark can remain on its own serial path. It provides a single Ethernet/PoE appliance while avoiding a shared RS485 multidrop bus during commissioning.

Reference topology:

```text
Sol-Ark #1 RS485 -> Waveshare CH1
Sol-Ark #2 RS485 -> Waveshare CH2
Waveshare Ethernet -> LAN -> Home Assistant
```

## Existing SolarAssistant cabling

If an existing installation used a SolarAssistant splitter at the Battery/CAN port, the splitter can remain in place when:

- the battery continues to communicate over CAN;
- the splitter's RS485 output was previously used successfully for inverter monitoring;
- the old USB/RS485 converter is removed from the monitoring path.

The new Waveshare gateway replaces the USB/RS485 electronics. It does not accept USB serial data.

## Cabling strategy

The cleanest approach is usually:

1. Leave the splitter at the inverter.
2. Leave the battery CAN cable unchanged.
3. Unplug the old SolarAssistant USB/RS485 cable from the splitter's RS485 female RJ45 jack.
4. Insert a passive RJ45 patch cable.
5. Terminate the three required RS485 conductors at the Waveshare A/B/GND terminals.

Do not assume conductor color without continuity testing.

## Multimeter requirements

A basic digital multimeter is sufficient for commissioning tasks:

- identify RJ45 pin-to-wire continuity;
- verify no shorts between A, B, and GND;
- check termination resistance with equipment powered off;
- confirm cable integrity.

## Termination

The public Sol-Ark V1.4 document states:

- the inverter is internally terminated;
- a 120-ohm resistor should be installed at the master side.

Before adding an external resistor, determine whether the Waveshare provides built-in or switchable termination. Do not intentionally place two separate 120-ohm resistors in parallel at the same physical gateway end.

With a normally terminated point-to-point RS485 link powered off, two 120-ohm end terminators appear approximately as 60 ohms across A/B. Treat that as a diagnostic clue rather than an absolute requirement because connected electronics can affect resistance readings.

## PoE considerations

PoE is useful because it reduces local power wiring at the gateway. The gateway's Ethernet link should terminate at a standards-compliant PoE switch or injector appropriate for the selected Waveshare version.

If PoE is not used, follow the Waveshare power-input requirements for the exact hardware revision.

## Installation location

Prefer a location that is:

- electrically protected;
- dry or appropriately enclosed;
- close enough to the inverter RS485 cabling to avoid unnecessary serial runs;
- connected to the same trusted LAN/VLAN as Home Assistant or routable to it;
- accessible for commissioning and termination checks.

## Network security

Treat the Waveshare as an infrastructure device:

- assign a static IP or DHCP reservation;
- use a trusted network/VLAN;
- restrict unneeded inbound access where practical;
- document each channel IP and purpose;
- do not expose TCP 502 directly to the public Internet.

## Recommended labels

Label both ends of each cable:

```text
SOLARK-1-RS485
SOLARK-2-RS485
WAVESHARE-CH1
WAVESHARE-CH2
```

Also record:

- inverter serial number;
- inverter firmware version;
- parallel role/Modbus SN;
- Waveshare channel IP;
- MAC address;
- cable termination arrangement.

## Hardware not required

This architecture does not require:

- SolarAssistant computer;
- USB-to-RS485 adapters after migration;
- Sol-Ark cloud monitoring for local HA telemetry;
- a Solarman/Wi-Fi dongle for this data path;
- MQTT between the inverter and Home Assistant.

MQTT may still be used elsewhere in the broader Home Assistant environment, but it is not required for the native Modbus path.
