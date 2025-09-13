class Config:
    # Default parameters that can be overridden by the GUI
    def __init__(self):
        # Satellite parameters
        self.SATELLITE_POWER = 40  # dBW
        self.SATELLITE_ANTENNA_GAIN = 30  # dBi
        self.FREQUENCY = 12e9  # Hz (Ku-band)
        
        # Ground station parameters
        self.GROUND_ANTENNA_GAIN = 45  # dBi
        self.GROUND_NOISE_TEMP = 290  # Kelvin
        self.GROUND_SYSTEM_LOSSES = 2  # dB
        
        # Path parameters
        self.DISTANCE = 35786e3  # meters (GEO altitude)
        self.ATMOSPHERIC_LOSS = 0.5  # dB
        self.RAIN_MARGIN = 3  # dB
        
        # Modulation parameters
        self.MODULATION_SCHEME = "QPSK"
        self.SYMBOL_RATE = 25e6  # symbols/second
        self.ROLLOFF_FACTOR = 0.35
        
        # Coding parameters
        self.CODING_RATE = 0.75
        self.FEC_TYPE = "Repetition"
        
        # Simulation parameters
        self.NUM_BITS = 1000
        self.SNR_DB = 10