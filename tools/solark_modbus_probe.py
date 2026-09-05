#!/usr/bin/env python3
"""Read-only Sol-Ark 15K Modbus TCP commissioning probe.

No third-party modules are required.

Usage:
    python solark_modbus_probe.py 192.168.1.241
    python solark_modbus_probe.py 192.168.1.241 --port 502 --dump

Protocol basis: public Sol-Ark Modbus RTU Protocol V1.4
- Gateway transport: Modbus TCP -> Modbus RTU
- Unit/slave ID: 1
- Function: 3 (Read Holding Registers)

This utility contains no Modbus write functions.
"""

from __future__ import annotations

import argparse
import socket
import struct
import sys
import time

UNIT_ID = 1
FC_READ_HOLDING = 3


def read_exact(sock: socket.socket, count: int) -> bytes:
    data = b""
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise ConnectionError("Connection closed while receiving data")
        data += chunk
    return data


class ModbusTCP:
    def __init__(self, host: str, port: int = 502, timeout: float = 3.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.transaction_id = 0

    def read_holding(self, start: int, count: int) -> list[int]:
        if not 1 <= count <= 125:
            raise ValueError("Modbus FC3 register count must be 1..125")

        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        pdu = struct.pack(">BHH", FC_READ_HOLDING, start, count)
        # MBAP = transaction ID, protocol ID=0, length(unit+PDU), unit ID
        request = (
            struct.pack(">HHHB", self.transaction_id, 0, len(pdu) + 1, UNIT_ID)
            + pdu
        )

        with socket.create_connection((self.host, self.port), self.timeout) as sock:
            sock.settimeout(self.timeout)
            sock.sendall(request)
            mbap = read_exact(sock, 7)
            rx_tid, protocol, length, unit = struct.unpack(">HHHB", mbap)
            body = read_exact(sock, length - 1)

        if rx_tid != self.transaction_id:
            raise RuntimeError(
                f"Transaction ID mismatch: sent {self.transaction_id}, received {rx_tid}"
            )
        if protocol != 0:
            raise RuntimeError(f"Unexpected Modbus protocol ID {protocol}")
        if unit != UNIT_ID:
            raise RuntimeError(f"Unit ID mismatch: expected {UNIT_ID}, received {unit}")
        if not body:
            raise RuntimeError("Empty Modbus response")

        function = body[0]
        if function == (FC_READ_HOLDING | 0x80):
            code = body[1] if len(body) > 1 else None
            raise RuntimeError(f"Modbus exception response, code={code}")
        if function != FC_READ_HOLDING:
            raise RuntimeError(f"Unexpected function code {function}")

        byte_count = body[1]
        payload = body[2:]
        if byte_count != count * 2 or len(payload) != byte_count:
            raise RuntimeError(
                "Unexpected byte count: "
                f"expected {count * 2}, header={byte_count}, actual={len(payload)}"
            )

        return list(struct.unpack(">" + "H" * count, payload))


def s16(value: int) -> int:
    """Interpret a Modbus uint16 word as signed int16."""
    return value - 65536 if value & 0x8000 else value


def u32_low_high(low: int, high: int) -> int:
    """Combine Sol-Ark low-word/high-word ordering into an unsigned integer."""
    return (high << 16) | low


def fmt(value: float | int, unit: str = "", decimals: int | None = None) -> str:
    text = str(value) if decimals is None else f"{value:.{decimals}f}"
    return f"{text} {unit}".strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Sol-Ark 15K Modbus TCP probe"
    )
    parser.add_argument("host", help="Waveshare channel IP address")
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument(
        "--dump", action="store_true", help="Print all raw registers read"
    )
    args = parser.parse_args()

    modbus = ModbusTCP(args.host, args.port, args.timeout)

    print(f"Connecting to {args.host}:{args.port}, unit/slave 1, FC3...")
    try:
        # Two conservative reads cover the useful commissioning ranges.
        block_60 = modbus.read_holding(60, 55)   # 60..114
        time.sleep(0.15)
        block_150 = modbus.read_holding(150, 47)  # 150..196
    except Exception as exc:  # commissioning utility: show actionable error
        print(f"\nFAILED: {exc}", file=sys.stderr)
        print(
            "\nCheck TCP 502, Waveshare mode, 9600/8/N/1, "
            "A/B/GND, BMS mode 00, CAN battery communication, and termination."
        )
        return 2

    registers: dict[int, int] = {}
    registers.update({60 + i: value for i, value in enumerate(block_60)})
    registers.update({150 + i: value for i, value in enumerate(block_150)})

    def r(address: int) -> int:
        return registers.get(address, 0)

    metrics = [
        ("Grid frequency", r(79) * 0.01, "Hz", 2),
        ("Daily PV energy", r(108) * 0.1, "kWh", 1),
        ("PV1 voltage", r(109) * 0.1, "V", 1),
        ("PV1 current", r(110) * 0.1, "A", 1),
        ("PV2 voltage", r(111) * 0.1, "V", 1),
        ("PV2 current", r(112) * 0.1, "A", 1),
        ("PV3 voltage", r(113) * 0.1, "V", 1),
        ("PV3 current", r(114) * 0.1, "A", 1),
        ("Grid L1-N voltage", r(150) * 0.1, "V", 1),
        ("Grid L2-N voltage", r(151) * 0.1, "V", 1),
        ("Grid L1-L2 voltage", r(152) * 0.1, "V", 1),
        ("Inverter L1-N voltage", r(154) * 0.1, "V", 1),
        ("Inverter L2-N voltage", r(155) * 0.1, "V", 1),
        ("Load L1 voltage", r(157) * 0.1, "V", 1),
        ("Load L2 voltage", r(158) * 0.1, "V", 1),
        ("Grid total power", s16(r(169)), "W", 0),
        ("Inverter total power", s16(r(175)), "W", 0),
        ("Load total power", s16(r(178)), "W", 0),
        ("Generator port voltage", r(181) * 0.1, "V", 1),
        ("Battery temperature", r(182) * 0.1 - 100.0, "°C", 1),
        ("Battery voltage", r(183) * 0.01, "V", 2),
        ("Battery SOC", r(184), "%", 0),
        ("PV1 power", r(186), "W", 0),
        ("PV2 power", r(187), "W", 0),
        ("PV3 power", r(188), "W", 0),
        ("PV total calculated", r(186) + r(187) + r(188), "W", 0),
        ("Battery power (signed)", s16(r(190)), "W", 0),
        ("Battery current (signed)", s16(r(191)) * 0.01, "A", 2),
        ("Load frequency", r(192) * 0.01, "Hz", 2),
        ("Inverter frequency", r(193) * 0.01, "Hz", 2),
        ("Grid relay raw", r(194), "", 0),
        ("Generator relay raw", r(195), "", 0),
        ("Generator frequency", r(196) * 0.01, "Hz", 2),
        ("Heat-sink temperature", r(91) * 0.1 - 100.0, "°C", 1),
    ]

    print("\nREAD SUCCESSFUL\n")
    width = max(len(item[0]) for item in metrics)
    for name, value, unit, decimals in metrics:
        print(f"{name:<{width}} : {fmt(value, unit, decimals)}")

    fault_words = [r(103), r(104), r(105), r(106)]
    print("\nFault words 103..106 : " + " ".join(f"0x{x:04X}" for x in fault_words))
    if any(fault_words):
        print("WARNING: one or more fault bits are set.")
    else:
        print("No fault bits reported in registers 103..106.")

    total_batt_charge = u32_low_high(r(72), r(73)) * 0.1
    total_batt_discharge = u32_low_high(r(74), r(75)) * 0.1
    # Sol-Ark's grid-buy high word is register 80, not contiguous with 78.
    total_grid_buy = u32_low_high(r(78), r(80)) * 0.1
    total_grid_sell = u32_low_high(r(81), r(82)) * 0.1
    total_load = u32_low_high(r(85), r(86)) * 0.1
    total_pv = u32_low_high(r(96), r(97)) * 0.1

    print("\nENERGY COUNTERS")
    print(f"Total battery charge    : {total_batt_charge:.1f} kWh")
    print(f"Total battery discharge : {total_batt_discharge:.1f} kWh")
    print(f"Total grid import       : {total_grid_buy:.1f} kWh")
    print(f"Total grid export       : {total_grid_sell:.1f} kWh")
    print(f"Total load              : {total_load:.1f} kWh")
    print(f"Total PV                : {total_pv:.1f} kWh")

    if args.dump:
        print("\nRAW REGISTER DUMP")
        for address in sorted(registers):
            value = registers[address]
            print(f"{address:3d}: {value:5d}  0x{value:04X}")

    print("\nCompare these values to the Sol-Ark display before enabling long-term polling.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
