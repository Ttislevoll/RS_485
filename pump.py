class Compressor:
    def __init__(self, location, address, nom_value, tolerance):
        self.location = location
        self.address = address
        self.nom_value = nom_value
        self.tolerance = tolerance

    def __str__(self):
        location = "{:<20}".format(str(self.location))
        address = "{:<15}".format(str(self.address))
        nom_value = "{:<15}".format(str(self.nom_value))
        tolerance = "{:<15}".format(str(self.tolerance))
        return location + address + nom_value + tolerance