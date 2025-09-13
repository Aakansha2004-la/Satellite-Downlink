import streamlit as st
import numpy as np
import time
from config import Config
from modules.link_budget import LinkBudgetCalculator
from modules.modulation import Modulator
from modules.channel import SatelliteChannel
from modules.error_correction import ErrorCorrection
from modules.visualization import Visualizer
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Satellite Downlink Simulator",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stSlider > div > div > div {
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def simulate_ber_vs_snr(config, modulator, data_bits, encoded_bits, symbols):
    """Run BER vs SNR simulation"""
    snr_values = np.arange(0, 15, 1)
    ber_values = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, snr in enumerate(snr_values):
        status_text.text(f"Running simulation for SNR = {snr} dB...")
        
        # Create new channel instance for each SNR
        channel = SatelliteChannel(snr_db=snr)
        
        if config.FEC_TYPE == "Repetition":
            fec = ErrorCorrection(coding_rate=config.CODING_RATE)
        else:
            fec = ErrorCorrection(coding_rate=1.0)
        
        # Simulate channel
        received_symbols = channel.simulate_channel(symbols)
        received_bits = modulator.demodulate(received_symbols)
        decoded_bits = fec.decode(received_bits[:len(encoded_bits)])
        ber = fec.calculate_ber(data_bits, decoded_bits)
        ber_values.append(ber)
        
        progress_bar.progress((i + 1) / len(snr_values))
        time.sleep(0.01)  # Small delay to allow UI update
    
    status_text.text("Simulation complete!")
    progress_bar.empty()
    
    return snr_values, ber_values

def main():
    # Header
    st.markdown('<h1 class="main-header">🛰️ Satellite Downlink Simulator</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'run_simulation' not in st.session_state:
        st.session_state.run_simulation = False
    
    # Sidebar for parameters
    with st.sidebar:
        st.header("Simulation Parameters")
        
        # Satellite parameters
        st.subheader("Satellite Parameters")
        sat_power = st.slider("Satellite Power (dBW)", 20.0, 60.0, 40.0, 1.0)
        sat_antenna_gain = st.slider("Satellite Antenna Gain (dBi)", 20.0, 50.0, 30.0, 1.0)
        frequency = st.selectbox("Frequency Band", 
                                ["C-band (4 GHz)", "Ku-band (12 GHz)", "Ka-band (20 GHz)"])
        
        # Map frequency selection to value
        freq_map = {
            "C-band (4 GHz)": 4e9,
            "Ku-band (12 GHz)": 12e9,
            "Ka-band (20 GHz)": 20e9
        }
        frequency_value = freq_map[frequency]
        
        # Ground station parameters
        st.subheader("Ground Station Parameters")
        ground_antenna_gain = st.slider("Ground Antenna Gain (dBi)", 30.0, 60.0, 45.0, 1.0)
        ground_noise_temp = st.slider("Ground Noise Temperature (K)", 100.0, 500.0, 290.0, 10.0)
        ground_system_losses = st.slider("System Losses (dB)", 0.0, 5.0, 2.0, 0.1)
        
        # Path parameters
        st.subheader("Path Parameters")
        distance = st.selectbox("Satellite Altitude", 
                               ["LEO (500 km)", "MEO (10,000 km)", "GEO (35,786 km)"])
        
        dist_map = {
            "LEO (500 km)": 500e3,
            "MEO (10,000 km)": 10000e3,
            "GEO (35,786 km)": 35786e3
        }
        distance_value = dist_map[distance]
        
        atmospheric_loss = st.slider("Atmospheric Loss (dB)", 0.1, 5.0, 0.5, 0.1)
        rain_margin = st.slider("Rain Margin (dB)", 0.0, 10.0, 3.0, 0.5)
        
        # Modulation and coding
        st.subheader("Modulation and Coding")
        modulation_scheme = st.selectbox("Modulation Scheme", ["BPSK", "QPSK"])
        symbol_rate = st.slider("Symbol Rate (Msymbols/s)", 1.0, 100.0, 25.0, 1.0) * 1e6
        coding_rate = st.slider("Coding Rate", 0.1, 1.0, 0.75, 0.05)
        fec_type = st.selectbox("FEC Type", ["Repetition", "None"])
        
        # Simulation parameters
        st.subheader("Simulation Parameters")
        num_bits = st.slider("Number of Bits", 100, 5000, 1000, 100)
        snr_db = st.slider("SNR (dB)", 0.0, 20.0, 10.0, 0.5)
        
        # Run simulation button
        if st.button("Run Simulation", type="primary"):
            st.session_state.run_simulation = True
            st.rerun()
    
    # Initialize configuration with user parameters
    config = Config()
    config.SATELLITE_POWER = sat_power
    config.SATELLITE_ANTENNA_AIN = sat_antenna_gain
    config.FREQUENCY = frequency_value
    config.GROUND_ANTENNA_GAIN = ground_antenna_gain
    config.GROUND_NOISE_TEMP = ground_noise_temp
    config.GROUND_SYSTEM_LOSSES = ground_system_losses
    config.DISTANCE = distance_value
    config.ATMOSPHERIC_LOSS = atmospheric_loss
    config.RAIN_MARGIN = rain_margin
    config.MODULATION_SCHEME = modulation_scheme
    config.SYMBOL_RATE = symbol_rate
    config.CODING_RATE = coding_rate
    config.FEC_TYPE = fec_type
    config.NUM_BITS = num_bits
    config.SNR_DB = snr_db
    
    if st.session_state.run_simulation:
        try:
            # Initialize components
            link_budget = LinkBudgetCalculator(config)
            modulator = Modulator(config.MODULATION_SCHEME)
            channel = SatelliteChannel(snr_db=config.SNR_DB)
            
            if config.FEC_TYPE == "Repetition":
                fec = ErrorCorrection(coding_rate=config.CODING_RATE)
            else:
                fec = ErrorCorrection(coding_rate=1.0)  # No coding
            
            # Calculate link budget
            st.markdown('<div class="sub-header">Link Budget Analysis</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("EIRP", f"{link_budget.calculate_eirp():.2f} dBW")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Path Loss", f"{link_budget.calculate_free_space_loss():.2f} dB")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Received Power", f"{link_budget.calculate_received_power():.2f} dBW")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("C/N₀", f"{link_budget.calculate_cn0():.2f} dB-Hz")
                st.markdown('</div>', unsafe_allow_html=True)
            
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Eb/N₀", f"{link_budget.calculate_ebn0():.2f} dB")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col6:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                required_ebn0 = 9.6 if config.MODULATION_SCHEME == "QPSK" else 12.0
                margin = link_budget.calculate_link_margin(required_ebn0)
                st.metric("Link Margin", f"{margin:.2f} dB")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Link budget visualization
            link_params = {
                'EIRP': link_budget.calculate_eirp(),
                'Path Loss': -link_budget.calculate_free_space_loss(),
                'Rx Power': link_budget.calculate_received_power(),
                'C/N₀': link_budget.calculate_cn0(),
                'Eb/N₀': link_budget.calculate_ebn0()
            }
            
            fig = go.Figure(data=[
                go.Bar(x=list(link_params.keys()), y=list(link_params.values()))
            ])
            fig.update_layout(
                title="Link Budget Components",
                xaxis_title="Parameter",
                yaxis_title="Value (dB)",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Communication chain simulation
            st.markdown('<div class="sub-header">Communication Chain Simulation</div>', unsafe_allow_html=True)
            
            # Generate test data
            data_bits = np.random.randint(0, 2, config.NUM_BITS)
            
            # Apply error correction
            encoded_bits = fec.encode(data_bits)
            
            # Modulate
            symbols = modulator.modulate(encoded_bits)
            
            # Simulate channel
            received_symbols = channel.simulate_channel(symbols)
            
            # Demodulate
            received_bits = modulator.demodulate(received_symbols)
            
            # Decode
            decoded_bits = fec.decode(received_bits[:len(encoded_bits)])
            
            # Calculate BER
            ber = fec.calculate_ber(data_bits, decoded_bits)
            
            col9, col10, col11 = st.columns(3)
            
            with col9:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Original Bits", config.NUM_BITS)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col10:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                errors = np.sum(data_bits != decoded_bits)
                st.metric("Bit Errors", errors)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col11:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Bit Error Rate", f"{ber:.6f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Constellation diagram
            st.markdown('<div class="sub-header">Constellation Diagram</div>', unsafe_allow_html=True)
            
            # Create a Plotly figure for the constellation diagram
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Transmitted", "Received"))
            
            # Add transmitted symbols (first 200)
            fig.add_trace(
                go.Scatter(
                    x=np.real(symbols[:200]), 
                    y=np.imag(symbols[:200]),
                    mode='markers',
                    name='Transmitted',
                    marker=dict(color='blue', opacity=0.6)
                ),
                row=1, col=1
            )
            
            # Add received symbols (first 200)
            fig.add_trace(
                go.Scatter(
                    x=np.real(received_symbols[:200]), 
                    y=np.imag(received_symbols[:200]),
                    mode='markers',
                    name='Received',
                    marker=dict(color='red', opacity=0.6)
                ),
                row=1, col=2
            )
            
            # Update layout
            fig.update_layout(
                height=500,
                showlegend=False,
                template="plotly_white"
            )
            
            fig.update_xaxes(title_text="In-phase", row=1, col=1)
            fig.update_yaxes(title_text="Quadrature", row=1, col=1)
            fig.update_xaxes(title_text="In-phase", row=1, col=2)
            fig.update_yaxes(title_text="Quadrature", row=1, col=2)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # BER vs SNR simulation
            st.markdown('<div class="sub-header">BER vs SNR Performance</div>', unsafe_allow_html=True)
            
            # Run simulation for multiple SNR values
            snr_values, ber_values = simulate_ber_vs_snr(config, modulator, data_bits, encoded_bits, symbols)
            
            # Plot BER curve
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=snr_values, 
                y=ber_values,
                mode='lines+markers',
                name='Simulated BER',
                line=dict(width=2)
            ))
            
            # Add theoretical BER for comparison
            if config.MODULATION_SCHEME == "BPSK":
                theoretical_ber = 0.5 * np.erfc(np.sqrt(10**(snr_values/10)))
                fig.add_trace(go.Scatter(
                    x=snr_values, 
                    y=theoretical_ber,
                    mode='lines',
                    name='Theoretical BPSK BER',
                    line=dict(dash='dash')
                ))
            elif config.MODULATION_SCHEME == "QPSK":
                theoretical_ber = 0.5 * np.erfc(np.sqrt(10**(snr_values/10)))
                fig.add_trace(go.Scatter(
                    x=snr_values, 
                    y=theoretical_ber,
                    mode='lines',
                    name='Theoretical QPSK BER',
                    line=dict(dash='dash')
                ))
            
            fig.update_layout(
                title="Bit Error Rate vs SNR",
                xaxis_title="SNR (dB)",
                yaxis_title="Bit Error Rate",
                yaxis_type="log",
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display sample of transmitted and received bits
            st.markdown('<div class="sub-header">Transmitted vs Received Bits</div>', unsafe_allow_html=True)
            
            col12, col13 = st.columns(2)
            
            with col12:
                st.write("**First 20 Transmitted Bits:**")
                st.write(data_bits[:20])
            
            with col13:
                st.write("**First 20 Received Bits:**")
                st.write(decoded_bits[:20])
                
        except Exception as e:
            st.error(f"An error occurred during simulation: {str(e)}")
            st.info("Please try adjusting parameters or restarting the application.")
    
    else:
        # Show instructions when simulation hasn't been run
        st.info("👈 Adjust parameters in the sidebar and click 'Run Simulation' to start")
        
        # Display information about the simulator
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📡 About Satellite Downlinks
            
            A satellite downlink is the radio signal transmitted from a satellite to a ground station. 
            Key components include:
            
            - **Transmitter**: Satellite with power amplifier and antenna
            - **Path**: Free space with path loss and atmospheric effects
            - **Receiver**: Ground station with antenna and low-noise amplifier
            
            This simulator models the complete communication chain to help understand how different
            parameters affect link performance.
            """)
        
        with col2:
            st.markdown("""
            ### 🔧 Key Parameters
            
            **Satellite Parameters**:
            - Transmit power and antenna gain determine EIRP
            - Higher frequency means higher path loss
            
            **Path Parameters**:
            - Distance affects free space path loss
            - Atmospheric absorption and rain cause additional losses
            
            **Receiver Parameters**:
            - Antenna gain and noise temperature determine sensitivity
            - Modulation and coding affect spectral efficiency and robustness
            """)
        
        st.markdown("""
        ### 📊 Performance Metrics
        
        The simulator calculates:
        
        - **Link Budget**: EIRP, path loss, received power, C/N₀, Eb/N₀
        - **Bit Error Rate**: Probability of bit errors after demodulation
        - **Constellation Diagram**: Visual representation of modulated symbols
        - **BER vs SNR Curve**: Performance across different signal qualities
        """)

if __name__ == "__main__":
    main()