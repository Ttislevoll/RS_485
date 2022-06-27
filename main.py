import struct
data = b'\x68\x0b\x0b\x68\x01\x7e\x08\xdf\x53\x33\x44\x65\x1e\x09\x42\xfe\x16'
distance = struct.unpack('f', data[7:11])
print(distance)
temperature = struct.unpack('f', data[11:15])
print(temperature)