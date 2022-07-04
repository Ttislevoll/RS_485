class Sensor:
    def __init__(self, sensor_location):
        self.sensor_location = sensor_location
        self.values = {
            "Temperature": "",
            "Distance": "",
            "Serial Number": "",
            "SW Version": "",
            "Article Number": "",
            "Description": "",
            "Address": "",
            "Measuring Unit": "",
            "Measuring Offset": "",
            "Measuring Range": "",
        }
        # self.article_number = ""
        # self.description = ""
        # self.serial_number = ""
        # self.sw_version = ""
        # self.address = ""
        # self.measuring_unit = ""
        # self.measuring_range = ""
        # self.measuring_offset = ""
        # self.distance = ""
        # self.temperature = ""

    def __str__(self):
        return str(self.sensor_location)
    
    