class Sensor:
    def __init__(self, location, address, nom_value, tolerance):
        self.location = location
        self.address = address
        self.nom_value = nom_value
        self.tolerance = tolerance
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

    def __str__(self):
        return self.location
    
    