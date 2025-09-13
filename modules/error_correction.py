import numpy as np

class ErrorCorrection:
    def __init__(self, coding_rate=0.75):
        self.coding_rate = coding_rate
    
    def encode(self, data_bits):
        """Simple repetition coding (for demonstration)"""
        if self.coding_rate >= 0.99:  # No coding
            return data_bits.copy()
            
        repetition = int(1/self.coding_rate)
        encoded_bits = []
        for bit in data_bits:
            encoded_bits.extend([bit] * repetition)
        return np.array(encoded_bits)
    
    def decode(self, received_bits):
        """Majority voting decoding"""
        if self.coding_rate >= 0.99:  # No coding
            return received_bits.copy()
            
        repetition = int(1/self.coding_rate)
        decoded_bits = []
        
        for i in range(0, len(received_bits), repetition):
            segment = received_bits[i:i+repetition]
            # Use soft decision if values are not binary
            if np.any((segment != 0) & (segment != 1)):
                decoded_bit = 1 if np.mean(segment) > 0.5 else 0
            else:
                decoded_bit = 1 if np.sum(segment) > len(segment)/2 else 0
            decoded_bits.append(decoded_bit)
        
        return np.array(decoded_bits)
    
    def calculate_ber(self, original_bits, received_bits):
        """Calculate Bit Error Rate"""
        if len(original_bits) != len(received_bits):
            min_len = min(len(original_bits), len(received_bits))
            original_bits = original_bits[:min_len]
            received_bits = received_bits[:min_len]
            
        errors = np.sum(original_bits != received_bits)
        return errors / len(original_bits) if len(original_bits) > 0 else 0