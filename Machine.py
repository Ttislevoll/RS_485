from Sensor import Sensor
from compressor import Compressor
from typing import List

class Machine:
    def __init__(self, itm_number, description, serial_number, machine_type):
        self.itm_number = itm_number
        self.description = description
        self.serial_number = serial_number
        self.machine_type = machine_type
        self.sensors: List[Sensor] = []
        self.compressors = self.get_compressors()
        self.pumps = self.get_pumps()
    
    def __str__(self):
        return str(self.description)

    def get_compressors():
        lines = open("compressors.txt").readlines()
        list = []
        for line in lines:
            if line != '\n':
                list.append(Compressor(line.split()[0],line.split()[1],line.split()[2],line.split()[3]))
        return list

    def get_pumps():
        lines = open("pumps.txt").readlines()
        list = []
        for line in lines:
            if line != '\n':
                list.append(Compressor(line.split()[0],line.split()[1],line.split()[2],line.split()[3]))
        return list


        