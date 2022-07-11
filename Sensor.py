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

    def ToString(self):
        output = f"Location: {self.location}\nDefault Address: {self.address}\nNom Value: {self.nom_value}\nTolerance: {self.tolerance}"
        for key in self.values:
            if self.values[key]:
                output += f"\n{key}: {self.values[key]}"
        return output
    
    