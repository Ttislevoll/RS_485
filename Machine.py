from Sensor import Sensor
from typing import List

class Machine:
    def __init__(self, itm_number, description, serial_number):
        self.itm_number = itm_number
        self.description = description
        self.serial_number = serial_number
        self.sensors: List[Sensor] = []
    
    def __str__(self):
        return str(self.description)

        