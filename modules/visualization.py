import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

class Visualizer:
    def __init__(self):
        plt.style.use('default')
    
    def plot_constellation(self, symbols, title="Received Constellation"):
        """Plot constellation diagram using Matplotlib"""
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(np.real(symbols), np.imag(symbols), alpha=0.6)
        ax.axhline(0, color='black', linestyle='--', linewidth=0.5)
        ax.axvline(0, color='black', linestyle='--', linewidth=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_title(title)
        ax.set_xlabel('In-phase')
        ax.set_ylabel('Quadrature')
        ax.axis('equal')
        
        # Convert to base64 for Streamlit
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{img_str}"
    
    def plot_ber_vs_snr(self, snr_values, ber_values, theoretical_ber=None):
        """Plot BER vs SNR curve using Matplotlib"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.semilogy(snr_values, ber_values, 'b-o', linewidth=2, label='Simulated BER')
        
        if theoretical_ber is not None:
            ax.semilogy(snr_values, theoretical_ber, 'r--', linewidth=2, label='Theoretical BER')
        
        ax.grid(True, which="both", ls="-", alpha=0.3)
        ax.set_xlabel('SNR (dB)')
        ax.set_ylabel('Bit Error Rate (BER)')
        ax.set_title('BER vs SNR Performance')
        ax.legend()
        
        # Convert to base64 for Streamlit
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{img_str}"
    
    def plot_link_budget(self, link_params):
        """Visualize link budget components using Matplotlib"""
        fig, ax = plt.subplots(figsize=(12, 6))
        components = list(link_params.keys())
        values = list(link_params.values())
        
        bars = ax.bar(components, values)
        ax.set_title("Link Budget Components")
        ax.set_ylabel("Value (dB)")
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   f'{value:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Convert to base64 for Streamlit
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{img_str}"
    
    def plot_comparison_constellation(self, transmitted, received):
        """Plot comparison of transmitted and received constellations"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Transmitted constellation
        ax1.scatter(np.real(transmitted), np.imag(transmitted), alpha=0.6, color='blue')
        ax1.axhline(0, color='black', linestyle='--', linewidth=0.5)
        ax1.axvline(0, color='black', linestyle='--', linewidth=0.5)
        ax1.grid(True, alpha=0.3)
        ax1.set_title('Transmitted Constellation')
        ax1.set_xlabel('In-phase')
        ax1.set_ylabel('Quadrature')
        ax1.axis('equal')
        
        # Received constellation
        ax2.scatter(np.real(received), np.imag(received), alpha=0.6, color='red')
        ax2.axhline(0, color='black', linestyle='--', linewidth=0.5)
        ax2.axvline(0, color='black', linestyle='--', linewidth=0.5)
        ax2.grid(True, alpha=0.3)
        ax2.set_title('Received Constellation')
        ax2.set_xlabel('In-phase')
        ax2.set_ylabel('Quadrature')
        ax2.axis('equal')
        
        plt.tight_layout()
        
        # Convert to base64 for Streamlit
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{img_str}"