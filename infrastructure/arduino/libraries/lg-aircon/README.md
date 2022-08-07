# LG Aircon Interface

An arduino library for management devices via IR signal.

## Supported Devices
* LG Airconditioner WHISEN SNC067BCW

## Dependency
* [z3t0 / Arduino-IRremote](https://github.com/z3t0/Arduino-IRremote)

## How to Use
```cpp
#include <LGAircon.h>
LGAircon aircon;
String command = "88C0051";  // Turn Off
aircon.send(strtol(command.c_str(), NULL, 16));
```
