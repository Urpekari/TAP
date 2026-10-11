#v2026.04c
import binascii

import serial, time, logging, TAP, traceback
from evdev import InputDevice, categorize, ecodes, list_devices

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:[%(levelname)s]:%(message)s',  # Clean format
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class TAP_CLI:
    def __init__(self, port, baudrate, timeout):
        if port is None:
            self.serial = None
        else:
            #print("Serial is temporarily disabled")
            self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def read_TAP_message(self):
        buffer = bytearray()

        while True:
            if self.serial.in_waiting > 0:
                logger.info("Message received")
                chunk_size = min(32,self.serial.in_waiting)
                print("Chunk size:"+str(chunk_size))
                chunk = self.serial.read(chunk_size)
                
                if not chunk:  
                    break
                buffer.extend(chunk)
                print(' '.join(f'{b:02x}' for b in buffer))

            if len(buffer) >2 and buffer[-2:] == b'\x55\xAA':
                break

            time.sleep(0.7)

        return TAP.TAP_message.unpack(buffer)
    
    def send_TAP_message(self, packed_bytes):
        if not self.serial or not self.serial.is_open:
            raise RuntimeError("Serial port not connected")
        self.serial.write(packed_bytes)
        print(f"Sent {len(packed_bytes)} bytes")


    def create_TAP_message(self):

        

        tID = int(input("Select TargetID:"))
        sID = int(input("Select SourceID:"))

        message_type_str = input("Select Message Type:\n\nACK(00)\nDIRECT_COMMAND(01)\nINDIRECT_COMMAND(02)\nTELEMETRY(10)\nNEGOTIATE_DATALINK(FE)\nTELEMETRY_DATALINK(FF)\n\nYour Selection:")
        match message_type_str:
            case "00":
                message_type=TAP.ACK
                payload = self.create_ACK_payload()
            case "01":
                message_type=TAP.DIRECT_COMMAND
                payload = self.create_direct_command_payload()
            case "02":
                message_type=TAP.INDIRECT_COMMAND
                payload = self.create_indirect_command_payload()
            case "10":
                message_type=TAP.TELEMETRY
                payload = self.create_telemetry_payload()
            case "FE":
                message_type=TAP.NEGOTIATE_DATALINK
                payload = self.create_negotiate_datalink_payload()
            case "FF":
                message_type=TAP.TELEMETRY_DATALINK
                payload = self.create_telemetry_datalink_payload()
            case _:
                print("That is not an option, so funny man!")
                return

        tap_message = TAP.TAP_message(tID,sID,message_type,payload)        
        return tap_message

    def create_ACK_payload(self):
        ack_type_str = input("Select Message Type:\n\nACK(00)\nNACK(01)\n\nYour Selection:")
        match ack_type_str:
            case "00":
                ack_type = 0x00
                token = 0x123456
                return TAP.ACKPayload(ack_type,token)
            case "01":
                ack_type = 0x01
                token = 0x123456
                return TAP.ACKPayload(ack_type,token)
            case _:
                print("That is not an option, so funny man!")
                return


    def create_direct_command_payload(self):
        #bools
        bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        arm = input("ARM bit[y/n]")
        if arm == "y":
            bits[0]=1
        elif arm == "n":
            bits[0]=0

        auto = input("AUTO bit[y/n]")
        if auto == "y":
            bits[1]=1
        elif auto == "n":
            bits[1]=0

        stab = input("STAB bit[y/n]")
        if stab == "y":
            bits[2]=1
        elif stab == "n":
            bits[2]=0

        navlight = input("NAVLIGHT bit[y/n]")
        if navlight == "y":
            bits[3]=1
        elif navlight == "n":
            bits[3]=0

        strobe = input("AUTO bit[y/n]")
        if strobe == "y":
            bits[4]=1
        elif strobe == "n":
            bits[4]=0

        land = input("LAND bit[y/n]")
        if land == "y":
            bits[5]=1
        elif land == "n":
            bits[5]=0

        comlossby = input("COMLOSSBY bit[y/n]")
        if comlossby == "y":
            bits[11]=1
        elif comlossby == "n":
            bits[11]=0

        loiter = input("LOITER bit[y/n]")
        if loiter == "y":
            bits[12]=1
        elif loiter == "n":
            bits[12]=0

        rth = input("RTH bit[y/n]")
        if rth == "y":
            bits[13]=1
        elif rth == "n":
            bits[13]=0
          
        bools = sum(bit << (15 - i) for i, bit in enumerate(bits))  
        
        #values
        values = []
        for i in range(1,123):
            data = int(input(f"Input {i} data for direct command:"))
            value = int(data*65535/100)
            values.append(value)

            check = input("Do you want to add another value?[y/n]")
            if check == "y":
                pass
            elif check == "n":
                break
        
        return TAP.DirectCommandPayload(bools,values)
            

    def create_indirect_command_payload(self):
        #bools
        bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        arm = input("ARM bit[y/n]")
        if arm == "y":
            bits[0]=1
        elif arm == "n":
            bits[0]=0

        auto = input("AUTO bit[y/n]")
        if auto == "y":
            bits[1]=1
        elif auto == "n":
            bits[1]=0

        stab = input("STAB bit[y/n]")
        if stab == "y":
            bits[2]=1
        elif stab == "n":
            bits[2]=0

        navlight = input("NAVLIGHT bit[y/n]")
        if navlight == "y":
            bits[3]=1
        elif navlight == "n":
            bits[3]=0

        strobe = input("AUTO bit[y/n]")
        if strobe == "y":
            bits[4]=1
        elif strobe == "n":
            bits[4]=0

        land = input("LAND bit[y/n]")
        if land == "y":
            bits[5]=1
        elif land == "n":
            bits[5]=0

        comlossby = input("COMLOSSBY bit[y/n]")
        if comlossby == "y":
            bits[11]=1
        elif comlossby == "n":
            bits[11]=0

        loiter = input("LOITER bit[y/n]")
        if loiter == "y":
            bits[12]=1
        elif loiter == "n":
            bits[12]=0

        rth = input("RTH bit[y/n]")
        if rth == "y":
            bits[13]=1
        elif rth == "n":
            bits[13]=0
          
        bools = sum(bit << (15 - i) for i, bit in enumerate(bits))  
        lat = float(input("Waypoint Latitude:"))
        lon = float(input("Waypoint Longitude:"))
        alt = int(input("Waypoint Altitude/Depth:"))
        rad = int(input("Waypoint Precission Radius:"))
        return TAP.IndirectCommandPayload(bools,lat,lon,alt,rad)


    def create_telemetry_payload(self):
        lat = float(input("Latitude:"))
        lon = float(input("Longitude:"))
        alt = int(input("Altitude/Depth:"))
        heading = int(input("Heading(º*10):"))
        roll = float(input("Roll:"))
        pitch = float(input("Pitch:"))

        return TAP.TelemetryPayload(lat,lon,alt,heading,roll,pitch)
    
    #def create_negotiate_datalink_payload(self):

    def create_telemetry_datalink_payload(self):
        print("Only for debug purposes, this should be done at NIC level, e.g. LoRa driver")
        rssi = int(input("RSSI:"))   
        snr = int(input("SNR:")) 
        rtt = int(input("RTT:")) 
        sent_pkts = int(input("SENT_PKTS:")) 
        delta_t = int(input("DELTA_T:")) 

        return TAP.TelemetryDatalinkPayload(rssi,snr,rtt,sent_pkts,delta_t)

    


        

def main():

    #Print top ASCII
    print("---------------------- TAP Debug Tool v2026.04c ----------------------")
    
    serial_device = input("Select serial device - Default: /dev/ttyACM0:")
    if serial_device == "":
        serial_device = "/dev/ttyACM0"
    
    baudrate_str = input("Select serial baud rate - Default: 9600:")
    if baudrate_str == "":
        baudrate = 9600
    else:
        baudrate = int(baudrate_str)
    
    timeout_str = input("Select serial timeout - Default: 1s:")
    if timeout_str == "":
        timeout = 1
    else:
        timeout = int(timeout_str)
    
    selection = input("Select function:\n\nSend(s)\nMonitor(m)\nController(c)\n\nYour Selection:")
    
    match selection:
        case "s":
            send(serial_device,baudrate,timeout)
        case "m":
            monitor(serial_device,baudrate,timeout)
        case "c":
            controller(serial_device,baudrate,timeout)
        case _: 
            print("That is not an option, so funny man!")
            return



def send(serial_device,baudrate,timeout):
    print("Send mode selected")

    print(f"Sending through device '{serial_device}', baudrate:{baudrate}, timeout: {timeout} :")

    #Init serial device
    tap_cli = TAP_CLI(port=serial_device,baudrate=baudrate,timeout=timeout)
    
    while True: 
        tap_message = tap_cli.create_TAP_message()
        logger.debug(f"Message Bytes:\n{tap_message.debug()}")
        logger.debug(f"Message Fields:\n{tap_message.object_debug()}")
        tap_cli.send_TAP_message(tap_message.packed_message)

        while 1:
            serial_line = TAP_CLI.serial.readline()
            print (serial_line) #for debug
            if len(serial_line) == 0:
                break



def monitor(serial_device,baudrate,timeout):
    print("Monitor mode selected")
    
    #Init serial device
    tap_cli = TAP_CLI(port=serial_device,baudrate=baudrate,timeout=timeout)
   
    #Infinite loop to monitor incoming messages
    while True:
        try:
            tap_message = tap_cli.read_TAP_message()
            logger.debug(f"Message Bytes:\n{tap_message.debug()}")
            logger.debug(f"Message Fields:\n{tap_message.object_debug()}")

        except Exception as e:
            print(f"Read error: {e}")
            traceback.print_exc()
            continue


def controller(serial_device,baudrate,timeout):
    
    tap_cli = TAP_CLI(port=serial_device,baudrate=baudrate,timeout=timeout)
    # Pick the first input device that looks like a controller
    for path in list_devices():
        dev = InputDevice(path)
        print(dev.path, dev.name)
        if "controller" in dev.name.lower() or "gamepad" in dev.name.lower() or "joystick" in dev.name.lower():
            gamepad = dev
            break
    else:
        raise RuntimeError("No controller found")

    print("Using:", gamepad.path, gamepad.name)
    
    caps = dev.capabilities()
    print("\n**Capabilities:**")
    for cap_type in caps:
        print(f"{cap_type}: {caps[cap_type]}")

    axis = {
    0: 'ls_x',      # ABS_X
    1: 'ls_y',      # ABS_Y  
    3: 'rs_x',      # ABS_RX
    4: 'rs_y',      # ABS_RY
    2: 'lt',        # ABS_Z (left trigger)
    5: 'rt',        # ABS_RZ (right trigger)
    16: 'dpad_x',   # ABS_HAT0X
    17: 'dpad_y',   # ABS_HAT0Y
    }

    CENTER_TOLERANCE = 200  # adjust as needed
    center = {
        'ls_x': 0,
        'ls_y': 0,
        'rs_x': 0,
        'rs_y': 0
    }

    tID = int(input("Select TargetID:"))
    sID = int(input("Select SourceID:"))

    try:
        while True:
            # Get snapshot TWICE per second
            state = get_moment_state(gamepad)
            
            # Apply center/tolerance
            for key in state:
                if key != "lt" and key != "rt":
                    value = state[key] - center[key]
                    if abs(value) <= CENTER_TOLERANCE:
                        value = 0
                    state[key] = value
            
            if state['ls_x']== 0 and state['ls_y'] == 0 and state['rs_x']==0 and state['rs_y'] == 0 and state['lt'] == 0 and state['rt'] == 0:
                pass
            else:
                #print(f"ls_x:{state['ls_x']:6} ls_y:{state['ls_y']:6} "
                #f"rs_x:{state['rs_x']:6} rs_y:{state['rs_y']:6}"
                #f"lt:{state['lt']:6} rt:{state['rt']:6}")

                channels = [state['ls_x']+32768,state['rs_x']+32768,state['ls_y']+32768,state['rs_y']+32768,0x0000,0x0000,int(state['lt']*(65535/255)),int(state['rt']*(65535/255))]
                payload = TAP.DirectCommandPayload(0x8000,channels)
                tap_message = TAP.TAP_message(tID,sID,TAP.DIRECT_COMMAND,payload)
                logger.debug(f"Message Bytes:\n{tap_message.debug()}")
                logger.debug(f"Message Fields:\n{tap_message.object_debug()}")
                tap_cli.send_TAP_message(tap_message.packed_message)
                tap_message_r = tap_cli.read_TAP_message()
                while 1:
                    serial_line = tap_cli.serial.readline()
                    print (serial_line) #for debug
                    if len(serial_line) == 0:
                        break
                
                logger.debug(f"Message Bytes:\n{tap_message_r.debug()}")
                logger.debug(f"Message Fields:\n{tap_message_r.object_debug()}")

            time.sleep(0.5)  # 2Hz

    except KeyboardInterrupt:
        pass


def get_moment_state(gamepad):
    try:
        # Quick drain (non-blocking)
        while True:
            event = gamepad.read_one()
            if event is None:
                break
    except BlockingIOError:
        pass
    
    return {
        'ls_x': gamepad.absinfo(0).value,           # ABS_X
        'ls_y': gamepad.absinfo(1).value,           # ABS_Y
        'rs_x': gamepad.absinfo(3).value,           # ABS_RX  
        'rs_y': gamepad.absinfo(4).value,            # ABS_RY
        'lt'  : gamepad.absinfo(2).value,
        'rt'  : gamepad.absinfo(5).value
    }


if __name__ == '__main__':
    main()  