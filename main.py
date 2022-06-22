import serial
import serial.tools.list_ports


def portfinder() -> str:
    """Finds the correct com"""
    portList = serial.tools.list_ports.comports()

    for port in portList:
        if "MOXA" in str(port.description):
            print(port)
            COM = port.device
            return COM

COM = portfinder()

ser = serial.Serial(COM, 9600, timeout = 1)

print (ser.write(b'\xff\xff'))
verdi = ser.read(1)
print(verdi)
print(COM)