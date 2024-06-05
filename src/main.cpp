#include <Arduino.h>
#include <BluetoothSerial.h>
#include <PacketSerial.h>
#include <command_interpreter/CommandInterpreter.h>
#include <communication/UARTComm.h>

BluetoothSerial     SerialBT;
PacketSerial_<COBS> packetSerial;
UARTComm*           uartCommInstance;
CommandInterpreter  interpreter;

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
    Serial.println("Transmission ended, starting execution...");
    interpreter.executeCommands(uartCommInstance->getCommandsMemory(), uartCommInstance->getReceivedLength());

#ifdef PRINT_COMMAND_EXEC_REPORT
    for (const auto& command : interpreter.getCommands())
    {
        Serial.print("Command: ");
        Serial.print(command.name.c_str());
        Serial.print(" Status: ");
        Serial.print(static_cast<int>(command.status));
        if (command.status == ExecutionStatus::Error)
        {
            Serial.print(" Error: ");
            Serial.print(command.error.c_str());
        }
        Serial.println();
    }
#endif // PRINT_COMMAND_EXEC_REPORT
}

void onError() { Serial.println("Transmission error"); }

void onReceiveComplete() { Serial.println("Reception complete"); }

void onDebugCallback(std::string str) { Serial.write(str.c_str()); }

// Example callback function for handling A0 commands
void handleA0(Command& command)
{
    Serial.println("Handling A0");
    for (const auto& param : command.parameters)
    {
        Serial.print("Parameter: ");
        Serial.println(param);
    }
}

// Example callback function for handling B2 commands
void handleB2(Command& command)
{
    Serial.println("Handling B2");
    for (const auto& param : command.parameters)
    {
        Serial.print("Parameter: ");
        Serial.println(param);
    }
}

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

    interpreter.registerCallback("A0", handleA0);
    interpreter.registerCallback("B2", handleB2);
}

void loop() { uartCommInstance->handleCommunication(); }
