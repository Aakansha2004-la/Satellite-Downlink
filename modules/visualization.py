import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Visualizer:
    def __init__(self):
        plt.style.use('default')
    
    def plot_constellation(self, symbols, title="Received Constellation"):
        """Plot constellation diagram using Plotly"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=np.real(symbols), 
            y=np.imag(symbols),
            mode='markers',
            marker=dict(size=6, opacity=0.6),
            name='Symbols'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='In-phase',
            yaxis_title='Quadrature',
            showlegend=False,
            template="plotly_white"
        )
        
        return fig
    
    def plot_ber_vs_snr(self, snr_values, ber_values, theoretical_ber=None):
        """Plot BER vs SNR curve using Plotly"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=snr_values, 
            y=ber_values,
            mode='lines+markers',
            name='Simulated BER',
            line=dict(width=2)
        ))
        
        if theoretical_ber is not None:
            fig.add_trace(go.Scatter(
                x=snr_values, 
                y=theoretical_ber,
                mode='lines',
                name='Theoretical BER',
                line=dict(dash='dash', width=2)
            ))
        
        fig.update_layout(
            title='BER vs SNR Performance',
            xaxis_title='SNR (dB)',
            yaxis_title='Bit Error Rate (BER)',
            yaxis_type='log',
            template="plotly_white"
        )
        
        return fig
    
    def plot_link_budget(self, link_params):
        """Visualize link budget components using Plotly"""
        fig = go.Figure(data=[
            go.Bar(x=list(link_params.keys()), y=list(link_params.values()))
        ])
        
        fig.update_layout(
            title="Link Budget Components",
            xaxis_title="Parameter",
            yaxis_title="Value (dB)",
            template="plotly_white"
        )
        
        return fig
    
    def plot_comparison_constellation(self, transmitted, received):
        """Plot comparison of transmitted and received constellations"""
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Transmitted", "Received"))
        
        fig.add_trace(go.Scatter(
            x=np.real(transmitted), 
            y=np.imag(transmitted),
            mode='markers',
            name='Transmitted',
            marker=dict(color='blue', size=6, opacity=0.6)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=np.real(received), 
            y=np.imag(received),
            mode='markers',
            name='Received',
            marker=dict(color='red', size=6, opacity=0.6)
        ), row=1, col=2)
        
        fig.update_xaxes(title_text="In-phase", row=1, col=1)
        fig.update_yaxes(title_text="Quadrature", row=1, col=1)
        fig.update_xaxes(title_text="In-phase", row=1, col=2)
        fig.update_yaxes(title_text="Quadrature", row=1, col=2)
        
        fig.update_layout(
            height=500,
            showlegend=False,
            template="plotly_white"
        )
        
        return fig