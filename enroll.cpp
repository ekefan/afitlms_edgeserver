// ESP32_RFID_Enrollment_Sketch.ino (Code for the ESP32 microcontroller)

#include <SPI.h>
#include <MFRC522.h> // Make sure you have the MFRC522 library installed (e.g., from Miguel Balboa)

// Pin definitions for RC522 (Standard connections for ESP32 with MFRC522)
#define SS_PIN 5  // SDA (SS) pin
#define RST_PIN 27 // RST pin

MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance

String serialCommand = ""; // Buffer to store incoming serial data from PC
bool commandReady = false;

void setup() {
  Serial.begin(115200); // Initialize serial communication with the PC (USB)
  while (!Serial);     // Wait for serial port to connect. Needed for native USB.

  SPI.begin();       // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522 module

  Serial.println("ESP32: Ready. Waiting for commands from PC...");
  Serial.println("ESP32: Send 'SCAN_RFID:<user_id>:<user_name>' to start enrollment.");
}

void loop() {
  // Read incoming serial data from PC
  while (Serial.available()) {
    char inChar = Serial.read();
    serialCommand += inChar;
    if (inChar == '\n') { // Check for newline character to signify end of command
      commandReady = true;
    }
  }

  if (commandReady) {
    String command = serialCommand;
    serialCommand = ""; // Clear the buffer for the next command
    commandReady = false;

    // Process the command received from PC
    if (command.startsWith("SCAN_RFID:")) {
      String payload = command.substring(10); // Extract "user_id:user_name\n"
      int firstColon = payload.indexOf(':');
      if (firstColon != -1) {
        String userId = payload.substring(0, firstColon);
        String userName = payload.substring(firstColon + 1);
        userName.trim(); // Remove trailing newline if present

        Serial.print("ESP32: Received enrollment command for User ID: ");
        Serial.print(userId);
        Serial.print(", Name: ");
        Serial.println(userName);
        Serial.println("ESP32: Ready for RFID scan. Please present an RFID card to the module...");
        Serial.println("ESP32: Waiting for RFID scan..."); // Acknowledgment for the PC

        String rfidUid = scanForRFID(); // Call the RFID scanning function

        if (rfidUid.length() > 0) {
          // Send the scanned UID back to the PC
          Serial.print("UID_SCANNED:"); // Important prefix for PC to parse
          Serial.println(rfidUid);
          Serial.println("ESP32: RFID scanned and UID sent. Waiting for next command...");
        } else {
          Serial.println("ESP32: RFID scan timed out or failed. No UID read.");
          // You might send an error code back to PC if needed
        }
      } else {
        Serial.println("ESP32: Invalid SCAN_RFID command format.");
      }
    } else {
      Serial.print("ESP32: Unknown command received: ");
      Serial.println(command);
    }
  }
}

// Function to scan for an RFID card and return its UID
String scanForRFID() {
  unsigned long startTime = millis();
  const unsigned long timeout = 25000; // 25 seconds timeout for RFID scan (give user time)

  while ((millis() - startTime) < timeout) {
    // Look for new cards
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      Serial.print("ESP32: Card detected, UID: ");
      String uidString = "";
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        uidString += (mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""); // Add leading zero for single hex digit
        uidString += String(mfrc522.uid.uidByte[i], HEX);        // Convert byte to hex string
      }
      uidString.toUpperCase(); // Ensure UID is uppercase hex string for consistency
      Serial.println(uidString);

      mfrc522.PICC_HaltA();      // Halt PICC (the tag) to prevent re-reading the same one immediately
      mfrc522.PCD_StopCrypto1(); // Stop encryption if it was active (good practice)
      return uidString;
    }
    delay(50); // Small delay to prevent busy-waiting and allow serial processing
  }
  return ""; // Return empty string if timeout
}