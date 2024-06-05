#include "UARTComm.h"
#include <Arduino.h>

UARTComm::UARTComm(Stream& serial, size_t chunkSize, PacketSerial& packetSerial)
    : serial(serial),
      packetSerial(packetSerial),
      chunkSize(chunkSize),
      receivedData(nullptr),
      receivedLength(0),
      currentState(WAITING_FOR_SIZE),
      onTransmitStart(nullptr),
      onTransmitEnd(nullptr),
      onError(nullptr),
      onReceiveComplete(nullptr),
      onDebugCallback(nullptr)
{
}

void UARTComm::begin() { packetSerial.setStream(&serial); }

void UARTComm::handleCommunication() { packetSerial.update(); }

void UARTComm::allocateMemory(size_t size)
{

    receivedData = (uint8_t*)malloc(size);
    onDebugCallback("Allocated " + std::to_string(size) + " bytes\n");

    if (receivedData == nullptr)
    {
        if (onError)
            onError();
        return;
    }

    receivedLength = 0;
    if (onTransmitStart)
        onTransmitStart();
}

void UARTComm::processReceivedChunk(const uint8_t* buffer, size_t size)
{
    uint32_t receivedCRC = *(uint32_t*)(buffer + size - 4);
    onDebugCallback("Chunk recieved, calculating CRC...\n");
    uint32_t calculatedCRC = crc.calculate(buffer, size - 4);

    for (int i = 0; i < size; i++)
        Serial.printf("%X ", buffer[i]);

    onDebugCallback("\nRecieved CRC: ");
    Serial.printf("%08X\n", receivedCRC);
    onDebugCallback("Calculated CRC: ");
    Serial.printf("%08X\n", calculatedCRC);

    if (receivedCRC == calculatedCRC)
    {
        sendString("ACK");
        onDebugCallback("Memory offset: " + std::to_string(receivedLength) + "\n");
        memcpy(receivedData + receivedLength, buffer, (size - 4));
        receivedLength += (size - 4);
    }
    else
    {
        sendString("ERR");
        receivedLength = 0; // Reset offset to retry
    }
}

void UARTComm::sendString(std::string str)
{
    uint8_t buf[str.length()];
    memcpy(buf, str.c_str(), sizeof(buf));
    packetSerial.send(buf, sizeof(buf));
}

void UARTComm::handlePacketReceived(const uint8_t* buffer, size_t size)
{
    switch (currentState)
    {
    case WAITING_FOR_SIZE:
        if (size >= 4)
        {
            totalDataSize = *((size_t*)buffer);
            currentState  = ALLOCATING_MEMORY;
            onDebugCallback("RECEIVING_SIZE_INFO\n");
            onDebugCallback("Size: " + std::to_string(totalDataSize) + "\n");
        }
    case ALLOCATING_MEMORY:
        allocateMemory(totalDataSize);
        onDebugCallback("ALLOCATING_MEMORY\n");
        sendString("SIZE_ACK");
        currentState = RECEIVING_DATA;
        break;

    case RECEIVING_DATA:
        onDebugCallback("RECEIVING_DATA\n");
        onDebugCallback("Size: " + std::to_string(size) + "\n");

        processReceivedChunk(buffer, size);

        if (receivedLength < totalDataSize)
            onDebugCallback("Data copied\n");
        break;
    }

    if (receivedLength >= totalDataSize)
    {
        if (onReceiveComplete)
        {
            for (unsigned int i = 0; i < totalDataSize; i++)
                Serial.write(receivedData[i]);
            Serial.print("\n");
            onReceiveComplete();
        }
        if (onTransmitEnd)
            onTransmitEnd();
#ifdef DEALLOCATE_ONRECIEVE_COMPLETE
        free(receivedData);
        receivedData = nullptr;
#endif // DEALLOCATE_ONRECIEVE_COMPLETE
        totalDataSize = 0;
        currentState  = WAITING_FOR_SIZE;
    }
}

uint8_t* UARTComm::getCommandsMemory() { return receivedData; }

size_t UARTComm::getReceivedLength() { return receivedLength; }

void UARTComm::setOnTransmitStart(void (*callback)()) { onTransmitStart = callback; }

void UARTComm::setOnTransmitEnd(void (*callback)()) { onTransmitEnd = callback; }

void UARTComm::setOnError(void (*callback)()) { onError = callback; }

void UARTComm::setOnReceiveComplete(void (*callback)()) { onReceiveComplete = callback; }
void UARTComm::setOnDebugCallback(void (*callback)(std::string)) { onDebugCallback = callback; }

size_t UARTComm::available() { return serial.available(); }
