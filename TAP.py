import struct, logging
from crc import Calculator,Crc16

ACK = 0x00
DIRECT_COMMAND = 0x01
INDIRECT_COMMAND = 0x02
TELEMETRY = 0x10
NEGOTIATE_DATALINK = 0xFE
TELEMETRY_DATALINK = 0xFF


class TAP_message:
    def __init__(self, tID, sID, messageType, payload):
        self.header = TAP_header(tID,sID,messageType,0)
        self.payload = payload
        self.trailer = TAP_trailer()
        self.length = None
        self.packed_message = None
        

    def calculate_COBS(self):
        SOF_word_big_endian = 0xAA55
        msg = bytearray(self.packed_message)
        last_cobs_pos = 0x0006
        print(last_cobs_pos)
        for i in range(2, len(msg)-2):
            if(msg[i]<< 8 | msg[i+1]) == SOF_word_big_endian:
                print(f"FOUND ONE, i:{i}")
                msg[last_cobs_pos] = i >> 8
                msg[last_cobs_pos+1] = i 

                last_cobs_pos = i

            msg[last_cobs_pos] = 0x00
            msg[last_cobs_pos+1] = 0x00    

        self.packed_message = msg

    def pack_message(self):
        packed_payload = self.payload.pack_payload()
        
        self.header.messageLength = len(packed_payload)
        

        packed_header = self.header.pack_header()
        

        self.trailer.calculate_CRC16(packed_header, packed_payload)
        

        packed_trailer = self.trailer.pack_trailer()
        
        self.packed_message =  packed_header + packed_payload + packed_trailer
        self.calculate_COBS()
        return self.packed_message

        

        
class TAP_header:
    def __init__(self, tID, sID, messageType, messageLength):
        self.SOF = 0xAA55
        self.tID = tID
        self.sID = sID
        if messageType == DIRECT_COMMAND:
            self.messageLength = messageLength
        else:
            self.messageLength = 0x00

        self.messageType = messageType
        self.COBS = 0x0000

    def pack_header(self):

        return struct.pack('>HBBBBH',
            self.SOF,          
            self.tID,          
            self.sID,         
            self.messageLength,
            self.messageType,  
            self.COBS          
        )

class TAP_trailer:
    def __init__(self):
        self.CRC16 = None
        self.EOF = 0xAA55

    def calculate_CRC16(self, header_bytes, payload_bytes):
        #logging.DEBUG("Calculating CRC-16")
        data = header_bytes + payload_bytes
        calculator = Calculator(Crc16.MODBUS)
        self.CRC16 = calculator.checksum(data)

    def pack_trailer(self):

        return struct.pack('>HH',
            self.CRC16,
            self.EOF
        )

class TelemetryPayload:
    def __init__(self, lat, lon, alt, heading, roll, pitch):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.heading = heading
        self.roll = roll
        self.pitch = pitch
    
    def pack_payload(self):
        return struct.pack('>ffHhff',
            self.lat,        
            self.lon,      
            self.alt,         
            self.heading, 
            self.roll,  
            self.pitch          
        )



# THIS IS TURBO AI SLOP
CRC16 = 0xA001  # Assuming standard CRC-16 poly, adjust if different

def crc_16(message, message_len):
    out = 0
    bits_read = 0
    bit_flag = 0
    
    # Sanity check:
    if message is None or len(message) == 0:
        return 0
    
    # Convert message_len to actual bytes if it's a bytes object
    if isinstance(message, bytes):
        message_len = len(message)
    
    i = 0  # Byte index
    while message_len > 0:
        bit_flag = (out >> 15) & 1
        
        # Get next bit: work from LSB (item a)
        out = (out << 1) & 0xFFFF
        out |= (message[i] >> bits_read) & 1
        
        # Increment bit counter
        bits_read += 1
        if bits_read > 7:
            bits_read = 0
            i += 1
            message_len -= 1
        
        # Cycle check
        if bit_flag:
            out ^= CRC16
    
    # "Push out" the last 16 bits (item b)
    for _ in range(16):
        bit_flag = out >> 15
        out = (out << 1) & 0xFFFF
        if bit_flag:
            out ^= CRC16
    
    # Reverse the bits (item c)
    crc = 0
    bit_mask = 0x8000
    bit_pos = 0x0001
    while bit_mask != 0:
        if out & bit_mask:
            crc |= bit_pos
        bit_mask >>= 1
        bit_pos <<= 1
    
    return crc