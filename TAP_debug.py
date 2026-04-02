import serial
import time
import logging
import struct
import TAP

class TAP_CLI:
    def __init__(self,serial, baudRate, timeout):
        self.serial = serial
        self.baudRate = baudRate
        self.timeout = timeout
        

def main():

    tap_payload = TAP.TelemetryPayload(43.323228,-3.017115,0xAA55,245,90,90)
    tap_message = TAP.TAP_message(0x02,0x01,TAP.TELEMETRY,tap_payload)
    full_packet = tap_message.pack_message()
    print(f"Length: {len(full_packet)}")
    

    print("HEADER (8):", ' '.join(f'{b:02x}' for b in full_packet[0:8]))
    print("PAYLOAD(20):", ' '.join(f'{b:02x}' for b in full_packet[8:28]))
    print("TRAILER (4):", ' '.join(f'{b:02x}' for b in full_packet[28:32]))


if __name__ == '__main__':
    main()  