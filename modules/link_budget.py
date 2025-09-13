import numpy as np

class LinkBudgetCalculator:
    def __init__(self, config):
        self.config = config
        
    def calculate_free_space_loss(self):
        """Calculate free space path loss"""
        c = 3e8  # speed of light
        wavelength = c / self.config.FREQUENCY
        fsl = 20 * np.log10(4 * np.pi * self.config.DISTANCE / wavelength)
        return fsl
    
    def calculate_eirp(self):
        """Calculate Effective Isotropic Radiated Power"""
        return self.config.SATELLITE_POWER + self.config.SATELLITE_ANTENNA_GAIN
    
    def calculate_received_power(self):
        """Calculate received power at ground station"""
        eirp = self.calculate_eirp()
        fsl = self.calculate_free_space_loss()
        losses = self.config.ATMOSPHERIC_LOSS + self.config.RAIN_MARGIN + self.config.GROUND_SYSTEM_LOSSES
        
        received_power = eirp - fsl - losses + self.config.GROUND_ANTENNA_GAIN
        return received_power
    
    def calculate_cn0(self):
        """Calculate carrier-to-noise density ratio"""
        k = 1.38e-23  # Boltzmann's constant
        received_power_watts = 10**(self.calculate_received_power() / 10) / 1000  # Convert dBW to watts
        
        noise_density = k * self.config.GROUND_NOISE_TEMP
        cn0 = received_power_watts / noise_density
        return 10 * np.log10(cn0)
    
    def calculate_ebn0(self):
        """Calculate Eb/N0"""
        cn0 = 10**(self.calculate_cn0() / 10)
        
        # Calculate bits per symbol based on modulation
        if self.config.MODULATION_SCHEME == "BPSK":
            bits_per_symbol = 1
        elif self.config.MODULATION_SCHEME == "QPSK":
            bits_per_symbol = 2
        else:
            bits_per_symbol = 2  # Default to QPSK
        
        bit_rate = self.config.SYMBOL_RATE * bits_per_symbol
        ebn0 = cn0 / bit_rate
        return 10 * np.log10(ebn0)
    
    def calculate_link_margin(self, required_ebn0):
        """Calculate link margin"""
        actual_ebn0 = self.calculate_ebn0()
        return actual_ebn0 - required_ebn0