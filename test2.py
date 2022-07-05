from compressor import Compressor
compressors = []
temp = open("pumps.txt").readlines()
for x in temp:
    if x != '\n':
        compressors.append(Compressor(x.split()[0],x.split()[1],x.split()[2],x.split()[3]))

for c in compressors:
    print(c)

