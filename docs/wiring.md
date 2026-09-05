# Wiring Guide

## Scope

This guide covers the reference installation where each Sol-Ark 15K already has a CAN/RS485 splitter connected to the inverter's **Battery CAN Bus** port and the battery uses CAN communications.

The objective is to remove the failed SolarAssistant USB/RS485 interface while leaving the battery CAN path undisturbed.

## Sol-Ark 15K communication context

The public Sol-Ark V1.4 protocol describes the 15K Battery CAN Bus RJ45 as a combined connector carrying CAN and RS485 signals. The document also states that CAN-based battery communications may coexist with this read protocol when the inverter is configured appropriately.

For this project, the preferred path is the **RS485 output of the already-proven splitter**, not a new connection to a different inverter port.

## Existing arrangement

```text
Sol-Ark 15K Battery/CAN port
          |
          v
       Splitter
       /      \
      /        \
Battery CAN   RS485 monitoring
    |               |
 Battery       USB/RS485 cable
                     |
              SolarAssistant
```

## New arrangement

```text
Sol-Ark 15K Battery/CAN port
          |
          v
       Splitter
       /      \
      /        \
Battery CAN   RS485 monitoring
    |               |
 Battery       passive RJ45 lead
                     |
                     v
                Waveshare
                     |
                     v
                  Ethernet
                     |
                     v
              Home Assistant
```

## Splitter RS485 jack pinout

For the SolarAssistant-style Sol-Ark 15K splitter used by this project, the RS485 female RJ45 output is treated as:

| RJ45 pin | Signal | Waveshare terminal |
|---:|---|---|
| 1 | RS485 B | B- |
| 2 | RS485 A | A+ |
| 3 | GND | GND |

This is the **splitter-output pinout** used by the existing monitoring cable path. Do not confuse it with the raw pin table for the inverter's combined Battery CAN Bus connector.

## Passive cable construction

Use a normal straight-through Cat5e/Cat6 patch cable:

1. Plug the RJ45 male end into the splitter's RS485 female jack.
2. Cut the other end off.
3. Strip the jacket carefully.
4. Identify conductors by continuity to RJ45 pins 1, 2, and 3.
5. Terminate those conductors at the Waveshare.

For a standard T568B patch cord, the usual colors are:

| RJ45 pin | Typical T568B conductor |
|---:|---|
| 1 | White/Orange |
| 2 | Orange |
| 3 | White/Green |

**Always verify with a multimeter.** Do not rely solely on color.

## Channel 1 wiring

```text
Sol-Ark #1 splitter                Waveshare CH1
RS485 female RJ45

Pin 1  B  -----------------------> B-
Pin 2  A  -----------------------> A+
Pin 3  GND ----------------------> GND
```

## Channel 2 wiring

```text
Sol-Ark #2 splitter                Waveshare CH2
RS485 female RJ45

Pin 1  B  -----------------------> B-
Pin 2  A  -----------------------> A+
Pin 3  GND ----------------------> GND
```

## Ground is required

Do not omit the signal ground. The public Sol-Ark V1.4 protocol explicitly states that ground must be connected between inverter and master because communication may otherwise be disrupted by external noise.

This signal-reference conductor is part of the communications link. Follow the Waveshare documentation for its terminal naming and isolation arrangement.

## Termination

The Sol-Ark V1.4 document states that:

- the inverter already has internal termination;
- a 120-ohm termination resistor should be used at the master side.

Before adding a resistor:

1. determine whether the Waveshare channel has built-in/selectable 120-ohm termination;
2. avoid adding an additional resistor if the channel is already terminated;
3. power equipment off before making resistance measurements.

## Continuity-test procedure

Before connecting the Waveshare:

1. Unplug both ends of the passive patch lead.
2. Set the meter to continuity mode.
3. Identify RJ45 pin 1 at the plug.
4. Find the corresponding cut conductor and label it `B`.
5. Repeat for pin 2 and label it `A`.
6. Repeat for pin 3 and label it `GND`.
7. Confirm there is no continuity between A and B.
8. Confirm there is no continuity between A and GND.
9. Confirm there is no continuity between B and GND.

## First power-up wiring rule

Connect only **one inverter/channel** during initial commissioning.

Recommended order:

```text
1. Sol-Ark #1 splitter CAN -> battery stays connected
2. Sol-Ark #1 splitter RS485 -> Waveshare CH1
3. Waveshare CH2 left disconnected
4. Configure and validate CH1
5. Only after CH1 passes, connect CH2
```

## A/B polarity troubleshooting

RS485 A/B labeling is not perfectly consistent across manufacturers. The project wiring uses the documented splitter signals and Waveshare terminal labels. If TCP connectivity works but every Modbus request times out, verify:

- A to A+;
- B to B-;
- GND to GND;
- continuity and termination.

Only after those checks should A and B be swapped as a diagnostic step.

## Do not connect

Do not connect:

- the USB plug from the former SolarAssistant cable to the Waveshare;
- CAN-H or CAN-L to the Waveshare RS485 terminals;
- protective earth in place of the required RS485 signal reference unless the equipment documentation explicitly calls for that arrangement;
- the two inverter RS485 links together during the reference commissioning process.

## Recordkeeping

Document the final wiring in the installation notes:

```text
Inverter #1 splitter pin 1 -> CH1 B-
Inverter #1 splitter pin 2 -> CH1 A+
Inverter #1 splitter pin 3 -> CH1 GND

Inverter #2 splitter pin 1 -> CH2 B-
Inverter #2 splitter pin 2 -> CH2 A+
Inverter #2 splitter pin 3 -> CH2 GND
```

Also record whether the Waveshare internal termination was enabled or an external resistor was installed.
