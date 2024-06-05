#ifndef UARTCOMM_H
#define UARTCOMM_H

#include <Arduino.h>
#include <CRC32.h>
#include <PacketSerial.h>
#include <Stream.h>

class UARTComm
{
  public:
    UARTComm(Stream& serial, size_t chunkSize, PacketSerial& packetSerial);
    void     begin();
    void     handleCommunication();
    void     setOnTransmitStart(void (*callback)());
    void     setOnTransmitEnd(void (*callback)());
    void     setOnError(void (*callback)());
    void     setOnReceiveComplete(void (*callback)());
    void     setOnDebugCallback(void (*callback)(std::string));
    size_t   available();
    void     handlePacketReceived(const uint8_t* buffer, size_t size);
    uint8_t* getCommandsMemory();
    size_t   getReceivedLength();

  private:
    enum State
    {
        WAITING_FOR_SIZE,
        ALLOCATING_MEMORY,
        RECEIVING_DATA
    };
    Stream&       serial;
    PacketSerial& packetSerial;
    size_t        chunkSize;
    uint8_t*      receivedData;
    size_t        receivedLength;
    size_t        totalDataSize;
    State         currentState;
    CRC32         crc;

    void (*onTransmitStart)();
    void (*onTransmitEnd)();
    void (*onError)();
    void (*onReceiveComplete)();
    void (*onDebugCallback)(std::string str);

    void allocateMemory(size_t size);
    void processReceivedChunk(const uint8_t* buffer, size_t size);
    void sendString(std::string str);
};

#endif
