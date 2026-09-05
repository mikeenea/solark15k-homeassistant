# Waveshare Gateway Setup

## Target device

This project targets the **Waveshare 2-CH RS485 TO POE ETH (B)** gateway.

The reference design uses one RS485 channel per Sol-Ark 15K inverter.

## Recommended initial network plan

Example only:

```text
Channel 1 / Sol-Ark #1: 192.168.1.241:502
Channel 2 / Sol-Ark #2: 192.168.1.242:502
```

Use addresses appropriate for your LAN and preferably reserve them in DHCP or configure static addresses outside the DHCP pool.

## Serial settings

Configure both channels for:

```text
Baud rate: 9600
Data bits: 8
Parity: None
Stop bits: 1
```

These values come from the public Sol-Ark Modbus RTU Protocol V1.4.

## Protocol mode

For native Home Assistant Modbus, use:

```text
Modbus TCP <--> Modbus RTU
TCP port 502
```

Do not use transparent serial-over-TCP mode for the primary configuration unless testing demonstrates a specific need.

## Storage/polling mode

Use the Waveshare in **non-storage** Modbus gateway mode.

The gateway should translate requests from Home Assistant; it should not independently poll and cache the inverter while Home Assistant is also polling.

Conceptually:

```text
Home Assistant request
        |
        v
Waveshare translates TCP -> RTU
        |
        v
Sol-Ark responds
        |
        v
Waveshare translates RTU -> TCP
        |
        v
Home Assistant receives response
```

## Channel-by-channel commissioning

### Channel 1

1. Connect only Sol-Ark #1.
2. Configure CH1 IP address.
3. Configure 9600/8/N/1.
4. Select Modbus TCP ↔ RTU.
5. Confirm port 502.
6. Disable storage/autopolling behavior.
7. Save/reboot the channel if required.
8. Test TCP reachability.
9. Run the Python Modbus probe.

### Channel 2

Do not configure or connect CH2 until CH1 has proven stable.

Then repeat the same settings with a different IP address.

## TCP reachability test

From Windows PowerShell:

```powershell
Test-NetConnection 192.168.1.241 -Port 502
```

Expected result:

```text
TcpTestSucceeded : True
```

This confirms only that the Ethernet/TCP service is reachable. It does **not** confirm that the Sol-Ark is answering Modbus.

## Modbus endpoint model

The public Sol-Ark V1.4 map defines the inverter slave ID as `1`.

Therefore:

```text
CH1 endpoint: 192.168.1.241:502, slave 1
CH2 endpoint: 192.168.1.242:502, slave 1
```

Do not substitute the inverter's Parallel-screen Modbus SN as the slave ID for this map.

## Timeout settings

Recommended initial values in Home Assistant:

```text
timeout: 5 seconds
message wait: ~100 ms
scan interval: 10 seconds for live values
```

The objective during commissioning is stability, not maximum sample rate.

## Termination

The public Sol-Ark V1.4 protocol specifies a 120-ohm terminator at the master end and states the inverter is internally terminated.

Before adding a resistor, verify whether the Waveshare channel has built-in or selectable termination for the exact hardware revision.

Record the final condition in the installation notes:

```text
CH1 termination: internal Waveshare / external 120 ohm / other
CH2 termination: internal Waveshare / external 120 ohm / other
```

## Network isolation

Recommended controls:

- no public Internet port forwarding to TCP 502;
- restrict gateway management access to trusted networks;
- keep configuration credentials private;
- use firewall rules between VLANs if Home Assistant is separated from infrastructure devices;
- document both gateway addresses.

## Validation checklist

Before moving to Home Assistant, confirm:

- [ ] CH1 responds to ping or is otherwise reachable.
- [ ] TCP 502 is open.
- [ ] RS485 A/B/GND are connected.
- [ ] serial format is 9600/8/N/1.
- [ ] protocol mode is Modbus TCP ↔ RTU.
- [ ] storage/autopolling mode is disabled.
- [ ] correct termination is present.
- [ ] Sol-Ark BMS Lithium Batt mode is `00`.
- [ ] battery communication is CAN, not RS485.
- [ ] Python probe can read registers.

Do not proceed to dual-inverter aggregation until both channels independently pass this checklist.
