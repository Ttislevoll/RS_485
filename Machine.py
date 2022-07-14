from sensor import Sensor
from typing import List

class Machine:
    def __init__(self, itm_number, description, serial_number, machine_type):
        self.itm_number = itm_number
        self.description = description
        self.serial_number = serial_number
        self.machine_type = machine_type
        self.sensors: List[Sensor] = []
        self.sensors_group: List[Sensor] = []

        #creates dictionary for overview
        lines = open("compressors.txt").readlines()
        self.compressors = {}
        for line in lines:
            if line != '\n':
                self.compressors[line.split()[0]] = ["","",line.split()[1],"",line.split()[2],line.split()[3]]

        lines = open("pumps.txt").readlines()
        self.pumps = {}
        for line in lines:
            if line != '\n':
                self.pumps[line.split()[0]] = ["","",line.split()[1],"",line.split()[2],line.split()[3]]
    
    def __str__(self):
        return str(self.description)