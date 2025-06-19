import struct
import binascii
import typing
import re

class ETF:
    @staticmethod
    def decode(data: typing.Union[bytes, str]) -> typing.Any:
        if isinstance(data, str):
            data = binascii.unhexlify(data)
        if data[0] != 131:
            raise ValueError("Invalid ETF header")
        decoder = ETFDecoder(data)
        return decoder.decode()

    @staticmethod
    def encode(value: typing.Any) -> bytes:
        encoder = ETFEncoder()
        return b'\x83' + encoder.encodeTerm(value)

class ETFDecoder:
    def __init__(self, data: bytes) -> None:
        self._data: bytes = data
        self._pos: int = 1

    def _readByte(self) -> int:
        b = self._data[self._pos]
        self._pos += 1
        return b

    def _read(self, size: int) -> bytes:
        b = self._data[self._pos:self._pos + size]
        self._pos += size
        return b

    def _readUint16(self) -> int:
        return struct.unpack(">H", self._read(2))[0]

    def _readUint32(self) -> int:
        return struct.unpack(">I", self._read(4))[0]

    def _decodeAtom(self, length: int) -> typing.Any:
        s = self._read(length).decode('utf-8')
        if s == "false": return False
        if s == "true": return True
        if s == "nil": return None
        return s

    def _decodeTerm(self) -> typing.Any:
        tag = self._readByte()
        if tag == 104:
            arity = self._readByte()
            return tuple(self._decodeTerm() for _ in range(arity))
        if tag == 108:
            length = self._readUint32()
            lst = [self._decodeTerm() for _ in range(length)]
            _ = self._decodeTerm()
            return lst
        if tag == 106:
            return []
        if tag == 116:
            length = self._readUint32()
            return {self._decodeTerm(): self._decodeTerm() for _ in range(length)}
        if tag == 97:
            return self._readByte()
        if tag == 98:
            return struct.unpack(">i", self._read(4))[0]
        if tag == 100:
            length = self._readUint16()
            return self._decodeAtom(length)
        if tag == 109:
            length = self._readUint32()
            return self._read(length)
        if tag == 107:
            length = self._readUint16()
            return self._read(length).decode('utf-8')
        if tag == 115:
            length = self._readByte()
            return self._decodeAtom(length)
        if tag == 118:
            length = self._readUint16()
            return self._decodeAtom(length)
        if tag == 119:
            length = self._readByte()
            return self._decodeAtom(length)
        raise ValueError(f"Unsupported ETF tag: {tag}")

    def _convertBytes(self, obj: typing.Any) -> typing.Any:
        if isinstance(obj, dict):
            return {self._convertBytes(k): self._convertBytes(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convertBytes(i) for i in obj]
        if isinstance(obj, bytes):
            try: return obj.decode()
            except: return obj
        return obj

    def decode(self) -> typing.Any:
        return self._convertBytes(self._decodeTerm())

class ETFEncoder:
    _atomRe = re.compile(r'^[a-z0-9_]+$')

    def encodeTerm(self, obj: typing.Any) -> bytes:
        if obj is None:
            return self._encodeAtom("nil")
        if obj is True:
            return self._encodeAtom("true")
        if obj is False:
            return self._encodeAtom("false")
        if isinstance(obj, int):
            if 0 <= obj <= 255:
                return b'\x61' + struct.pack('B', obj)
            return b'\x62' + struct.pack('>i', obj)
        if isinstance(obj, float):
            return b'\x46' + struct.pack('>d', obj)
        if isinstance(obj, str):
            bval = obj.encode('utf-8')
            return b'\x6D' + struct.pack('>I', len(bval)) + bval
        if isinstance(obj, (bytes, bytearray)):
            bval = bytes(obj)
            return b'\x6D' + struct.pack('>I', len(bval)) + bval
        if isinstance(obj, (list, tuple)):
            length = len(obj)
            if length == 0:
                return b'\x6A'
            content = b''.join(self.encodeTerm(x) for x in obj)
            return b'\x6C' + struct.pack('>I', length) + content + b'\x6A'
        if isinstance(obj, dict):
            items = []
            for k, v in obj.items():
                if isinstance(k, str):
                    kb = k.encode('utf-8')
                elif isinstance(k, bytes):
                    kb = k
                else:
                    raise TypeError("Map keys must be str or bytes")
                items.append(b'\x6D' + struct.pack('>I', len(kb)) + kb)
                items.append(self.encodeTerm(v))
            buf = b''.join(items)
            return b'\x74' + struct.pack('>I', len(obj)) + buf
        raise TypeError(f"Unsupported type: {type(obj)}")

    def _encodeAtom(self, s: str) -> bytes:
        bval = s.encode('ascii')
        n = len(bval)
        if n < 256:
            return b'\x73' + struct.pack('B', n) + bval
        return b'\x76' + struct.pack('>H', n) + bval
