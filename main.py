
fcs = 0x48
adr = 0x16
broadcast = [0x10,0x7e,0x01,0x4c,0xac,0x16]
test = bytearray(broadcast)
sum=0
for x in range(1, len(broadcast)-2):
    sum += int(broadcast[x])

print(hex(sum % 256))
print(0x7f)
print(str(test[1]))
print(hex(broadcast[-2]))
 