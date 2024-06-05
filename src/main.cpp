#include <Arduino.h>
#include <BluetoothSerial.h>
#include <PacketSerial.h>
#include <communication/UARTComm.h>

BluetoothSerial     SerialBT;
PacketSerial_<COBS> packetSerial;
UARTComm*           uartCommInstance;

void packetHandler(const uint8_t* buffer, size_t size)
{
    if (uartCommInstance)
    {
        uartCommInstance->handlePacketReceived(buffer, size);
    }
}

void onTransmitStart() { Serial.println("Transmission started"); }

void onTransmitEnd()
{
    Serial.println("Transmission ended");
    // Process the received data here
}

void onError() { Serial.println("Transmission error"); }

void onReceiveComplete() { Serial.println("Reception complete"); }

void onDebugCallback(std::string str) { Serial.write(str.c_str()); }

void setup()
{
    Serial.begin(115200);
    // For BluetoothSerial
    SerialBT.begin("ESP32_BT"); // Bluetooth device name
    uartCommInstance = new UARTComm(SerialBT, 256, packetSerial);
    uartCommInstance->begin();
    packetSerial.setPacketHandler([](const uint8_t* buffer, size_t size)
                                  { uartCommInstance->handlePacketReceived(buffer, size); });

    uartCommInstance->setOnTransmitStart(onTransmitStart);
    uartCommInstance->setOnTransmitEnd(onTransmitEnd);
    uartCommInstance->setOnError(onError);
    uartCommInstance->setOnReceiveComplete(onReceiveComplete);
    uartCommInstance->setOnDebugCallback(onDebugCallback);
}

void loop() { uartCommInstance->handleCommunication(); }
