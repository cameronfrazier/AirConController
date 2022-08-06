# AirConController

## References

- https://github.com/r45635/HVAC-IR-Control
  - [Specification PDF](https://github.com/r45635/HVAC-IR-Control/blob/master/Protocol/Panasonic%20HVAC%20IR%20Protocol%20specification.pdf)

| Element | Unit | Value |
| --- | --- | --- |
| Header | us | 3500 |
| HeaderSpace | us | 1750 |
| Mark | us | 435 |
| Space0 | us | 435 |
| Space1 | us | 1300 |
| Modulation | Hz | 38000 |
| Delta | us | 200 |
| Bits | - | 216 |

# Specification Details

The first frame of the protocol is independent of the command that needs to be sent. This is an 8 bytes frame which value is 0x4004072000000060

The Data Frame is 19 bytes long and is defined as:

| Byte# | Name | Description |
| --- | --- | --- |
| 6 | MODE_SWITCH | Defines the mode and toggles unit on/off (open lool)
| 7 | TEMPERATURE | Defines a temperature range between 16 to 30 (int)
| 15 | TEMPERATURE_HALF | Defines if the temperature should have an additional 0.5°C added (=128). Also identifies the limit stops are applied (=2).
| 9 | SWING_FAN | Controls the fan power and direction (4:8, Fan; 0:4, Swing)
| 19 | CHECKSUM | CRC is the checksum of the previous 18 bytes modulo 256
