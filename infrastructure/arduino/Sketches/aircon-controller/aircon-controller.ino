#include <string.h>
#include <LGAircon.h>

LGAircon aircon;

void setup() {
  Serial.begin(115200);
}

char DELEMETER[] = ":";
char *getNextToken(char *command) {
  return strtok(command, DELEMETER);
}

bool isHexadecimal(String string) {
  for (char ch : string) {
    if (!isHexadecimalDigit(ch)) {
      return false;
    }
  }
  return true;
}

unsigned long strToHex(String string) {
  char *pos = NULL;
  return strtoul(string.c_str(), &pos, 16);
}

bool isInvalidPayload(String payload) {
  return payload == NULL || payload.length() != 7 || !isHexadecimal(payload);
}

void send(String payload) {
  if (isInvalidPayload(payload)) {
    Serial.print("Invalid Payload: payload must be 7 length hexadecimal, but got ");
    Serial.println(payload);
    return;
  }
  aircon.send(strToHex(payload));
}

void handleCommand(String command) {
  char *commandChar = command.c_str();
  String token = String(getNextToken(commandChar));
  if (token == NULL) {
    Serial.println("No Command: ");
    return;
  } else if (token.startsWith("AIRCON")) {
    send(String(getNextToken(NULL)));
  } else {
    Serial.println("Unknown Command: " + token);
  }
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readString();
    Serial.println("[>] " + input);
    handleCommand(input);
  }
}
