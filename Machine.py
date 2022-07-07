from sensor import Sensor
from typing import List

class Machine:
    def __init__(self, itm_number, description, serial_number, machine_type):
        self.itm_number = itm_number
        self.description = description
        self.serial_number = serial_number
        self.machine_type = machine_type
        self.sensors: List[Sensor] = []
    
    def __str__(self):
        return str(self.description)