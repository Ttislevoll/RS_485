class Compressor:
    def __init__(self, location, address, nom_value, tolerance):
        self.location = location
        self.address = address
        self.nom_value = nom_value
        self.tolerance = tolerance

    def __str__(self):
        return f'{self.location:<20}{self.address:<10}{self.nom_value:<10}{self.tolerance:<10}'