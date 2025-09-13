import numpy as np

class Modulator:
    def __init__(self, modulation_type="QPSK"):
        self.modulation_type = modulation_type
        
        # Define constellation mappings
        self.constellations = {
            "BPSK": {0: -1+0j, 1: 1+0j},
            "QPSK": {
                (0,0): (1+1j)/np.sqrt(2),
                (0,1): (1-1j)/np.sqrt(2),
                (1,0): (-1+1j)/np.sqrt(2),
                (1,1): (-1-1j)/np.sqrt(2)
            }
        }
    
    def modulate(self, bits):
        """Modulate bits to symbols"""
        if self.modulation_type == "BPSK":
            symbols = np.array([self.constellations["BPSK"][bit] for bit in bits])
        elif self.modulation_type == "QPSK":
            # Group bits into pairs
            if len(bits) % 2 != 0:
                bits = np.append(bits, 0)  # Pad if odd number
            
            symbols = []
            for i in range(0, len(bits), 2):
                symbol_bits = (bits[i], bits[i+1])
                symbols.append(self.constellations["QPSK"][symbol_bits])
            
            symbols = np.array(symbols)
        else:
            # Default to QPSK
            if len(bits) % 2 != 0:
                bits = np.append(bits, 0)
            
            symbols = []
            for i in range(0, len(bits), 2):
                symbol_bits = (bits[i], bits[i+1])
                symbols.append(self.constellations["QPSK"][symbol_bits])
            
            symbols = np.array(symbols)
        
        return symbols
    
    def demodulate(self, symbols):
        """Demodulate symbols to bits"""
        if self.modulation_type == "BPSK":
            bits = [1 if np.real(symbol) > 0 else 0 for symbol in symbols]
        elif self.modulation_type == "QPSK":
            bits = []
            for symbol in symbols:
                # Find closest constellation point
                min_dist = float('inf')
                best_bits = None
                
                for bit_pair, const_point in self.constellations["QPSK"].items():
                    dist = np.abs(symbol - const_point)
                    if dist < min_dist:
                        min_dist = dist
                        best_bits = bit_pair
                
                bits.extend(best_bits)
        else:
            # Default to QPSK demodulation
            bits = []
            for symbol in symbols:
                min_dist = float('inf')
                best_bits = None
                
                for bit_pair, const_point in self.constellations["QPSK"].items():
                    dist = np.abs(symbol - const_point)
                    if dist < min_dist:
                        min_dist = dist
                        best_bits = bit_pair
                
                bits.extend(best_bits)
        
        return np.array(bits)