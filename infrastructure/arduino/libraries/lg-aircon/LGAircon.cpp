#include <Arduino.h>
#include <IRremote.h>
#include "LGAircon.h"

IRsend irsend;

void LGAircon::send(unsigned long command) {
  Serial.print("LGAircon:send: ");
  Serial.println(command, HEX);
  irsend.sendLG(command, 28);
}
