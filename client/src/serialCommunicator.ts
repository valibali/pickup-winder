import { SerialPort, ReadlineParser, DelimiterParser } from "serialport";
import { Transform } from "stream";
import * as fs from "fs";
// @ts-ignore
import * as cobs from "cobs";
import * as crc32 from "crc-32";
import { setTimeout as delay } from "timers/promises";
import { COBSParser } from "./parser";

const CRC_SIZE = 4;
const COBS_BYTE = Buffer.from([0x00]);

class SerialCommunicator {
  public port: SerialPort;
  private chunkSize: number;
  private data: Buffer;
  private offset: number;
  private parser: Transform;

  constructor(
    portName: string,
    baudrate: number = 115200,
    chunkSize: number = 256
  ) {
    this.port = new SerialPort({
      path: portName,
      baudRate: baudrate,
      autoOpen: false,
    });
    this.chunkSize = chunkSize - (CRC_SIZE + COBS_BYTE.length + 1);
    this.data = this.readDataFromFile("commands.txt");
    this.offset = 0;
    this.parser = new COBSParser({ cobs_byte: Buffer.from([0x00]) });
    //this.parser = new DelimiterParser({ delimiter: Buffer.from([0x00]) });
    this.port.pipe(this.parser);
  }

  private readDataFromFile(filePath: string): Buffer {
    /**
     * Reads data from a file and returns it as a Buffer.
     *
     * @param {string} filePath - The path to the file to read.
     * @returns {Buffer} - The data read from the file.
     */
    return fs.readFileSync(filePath);
  }

  public async sendTotalSize(): Promise<void> {
    /**
     * Sends the total size of the data to the serial port.
     */
    const size = this.data.length;
    console.log(`Datasize: ${size}`);
    const sizeBuffer = Buffer.alloc(4);
    sizeBuffer.writeUInt32LE(size, 0);
    console.log("Size buffer: " + sizeBuffer.toString("hex"));
    const encodedSize = Buffer.concat([cobs.encode(sizeBuffer), COBS_BYTE]);
    console.log("Encoded size buffer: " + encodedSize.toString("hex"));
    await this.waitForPort();
    this.port.write(encodedSize);
  }

  public async sendNextChunk(): Promise<void> {
    /**
     * Sends the next chunk of data if available.
     */
    if (this.offset < this.data.length) {
      await this.sendChunk(this.offset);
      this.offset += this.chunkSize;
    } else {
      console.log("All data sent");
    }
  }

  private async sendChunk(offset: number): Promise<void> {
    /**
     * Sends a chunk of data starting from the given offset.
     *
     * @param {number} offset - The starting point of the chunk to be sent.
     */
    const end = Math.min(offset + this.chunkSize, this.data.length);
    const chunk = this.data.slice(offset, end);
    const crc = crc32.buf(chunk);
    const crcBuffer = Buffer.alloc(4);
    crcBuffer.writeInt32LE(crc, 0);
    console.log("CRC: " + crcBuffer.toString("hex"));
    const packet = Buffer.concat([chunk, crcBuffer]);
    console.log("Packet: " + packet.toString("hex"));
    const encodedPacket = Buffer.concat([cobs.encode(packet), COBS_BYTE]);
    await this.waitForPort();
    this.port.write(encodedPacket);
    console.log(`Chunk sent, offset: ${offset}, size ${packet.length}`);
  }

  public async waitForPort(): Promise<void> {
    /**
     * Waits until the serial port is available for writing.
     */
    while (!this.port.writable) {
      await delay(100);
    }
  }

  public async readResponse(): Promise<void> {
    /**
     * Reads responses from the serial port and acts accordingly.
     */

    this.parser.on("data", async (data) => {
      if (data.toString().length) {
        console.log("Response: " + data.toString());
        if (
          data.equals(Buffer.from("SIZE_ACK")) ||
          data.equals(Buffer.from("ACK"))
        ) {
          await this.sendNextChunk();
        } else {
          console.log(`Unknown response: ${data.toString()}`);
        }
      }
    });
  }
}

const signalHandler = () => {
  /**
   * Handles the signal for graceful termination.
   */
  console.log("Exiting program...");
  process.exit(0);
};

process.on("SIGINT", signalHandler);

const communicator = new SerialCommunicator("/dev/rfcomm0");

(async () => {
  communicator.port.open();
  await communicator.waitForPort();
  await communicator.sendTotalSize();
  await communicator.readResponse();
})();
