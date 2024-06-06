import { Transform, TransformCallback, TransformOptions } from "stream";
// @ts-ignore
import * as cobs from "cobs";

export interface COBSParserOptions extends TransformOptions {
  /** The delimiter on which to split incoming data. */
  delimiter?: string | Buffer | number[];
  /** Should the delimiter be included at the end of data. Defaults to `false` */
  cobs_byte: Buffer;
}

/**
 * A transform stream that emits data each time a byte sequence is received.
 * @extends Transform
 *
 * To use the `Delimiter` parser, provide a delimiter as a string, buffer, or array of bytes. Runs in O(n) time.
 */
export class COBSParser extends Transform {
  delimiter: Buffer;
  buffer: Buffer;
  cobs_byte: Buffer;

  constructor({
    cobs_byte,
    delimiter = cobs_byte,
    ...options
  }: COBSParserOptions) {
    super(options);

    if (cobs_byte === undefined) {
      throw new TypeError('"cobs_byte" is not a bufferable object');
    }

    if (cobs_byte.length === 0) {
      throw new TypeError('"cobs_byte" has a 0 or undefined length');
    }

    this.delimiter = Buffer.from(delimiter);
    this.buffer = Buffer.alloc(0);
    this.cobs_byte = Buffer.from(cobs_byte);
  }

  _transform(chunk: Buffer, encoding: BufferEncoding, cb: TransformCallback) {
    let data = Buffer.concat([this.buffer, chunk]);
    let position;
    while ((position = data.indexOf(this.delimiter)) !== -1) {
      const packet = data.slice(0, position);
      this.push(cobs.decode(packet));
      data = data.slice(position + this.delimiter.length);
    }
    this.buffer = data;
    cb();
  }

  _flush(cb: TransformCallback) {
    if (this.buffer.length > 0) {
      this.push(cobs.decode(this.buffer));
    }
    this.buffer = Buffer.alloc(0);
    cb();
  }
}
