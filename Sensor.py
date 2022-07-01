class Sensor:
    def __init__(self, sensor_location):
        self.sensor_location = sensor_location
        self.article_number = None
        self.description = None
        self.serial_number = None
        self.sw_version = None
        self.address = None
        self.measuring_unit = None
        self.measuring_range = None
        self.measuring_offset = None
        self.distance = None
        self.temperature = None

    def __str__(self):
        return str(self.sensor_location)
    
    