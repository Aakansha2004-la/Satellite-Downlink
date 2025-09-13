import numpy as np

class SatelliteChannel:
    def __init__(self, snr_db, phase_offset=0, frequency_offset=0):
        self.snr_db = snr_db
        self.phase_offset = phase_offset
        self.frequency_offset = frequency_offset
    
    def add_noise(self, signal):
        """Add AWGN noise to the signal"""
        signal_power = np.mean(np.abs(signal)**2)
        snr_linear = 10**(self.snr_db / 10)
        noise_power = signal_power / snr_linear
        
        # Generate complex Gaussian noise
        noise = np.sqrt(noise_power/2) * (np.random.randn(len(signal)) + 
                                        1j * np.random.randn(len(signal)))
        
        return signal + noise
    
    def add_phase_noise(self, signal):
        """Add phase noise to the signal"""
        phase_noise = np.exp(1j * self.phase_offset * np.random.randn(len(signal)))
        return signal * phase_noise
    
    def add_frequency_offset(self, signal, sample_rate):
        """Add frequency offset to the signal"""
        t = np.arange(len(signal)) / sample_rate
        freq_shift = np.exp(1j * 2 * np.pi * self.frequency_offset * t)
        return signal * freq_shift
    
    def simulate_channel(self, signal, sample_rate=None):
        """Simulate satellite channel effects"""
        # Add phase noise
        if self.phase_offset != 0:
            signal = self.add_phase_noise(signal)
        
        # Add frequency offset if sample rate is provided
        if sample_rate is not None and self.frequency_offset != 0:
            signal = self.add_frequency_offset(signal, sample_rate)
        
        # Add AWGN noise
        signal = self.add_noise(signal)
        
        return signal