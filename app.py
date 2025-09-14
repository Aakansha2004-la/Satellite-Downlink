import streamlit as st
import numpy as np
import time
import base64
from config import Config
from modules.link_budget import LinkBudgetCalculator
from modules.modulation import Modulator
from modules.channel import SatelliteChannel
from modules.error_correction import ErrorCorrection
from modules.visualization import Visualizer

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
</style>
""", unsafe_allow_html=True)

def display_image_from_base64(base64_string):
    """Display base64 encoded image in Streamlit"""
    st.markdown(f'<img src="{base64_string}" style="max-width:100%;">', unsafe_allow_html=True)

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
        frequency = st.selectbox("Frequency Band", ["C-band (4 GHz)", "Ku-band (12 GHz)", "Ka-band (20 GHz)"])
        
        # Map frequency selection to value
        freq_map = {"C-band (4 GHz)": 4e9, "Ku-band (12 GHz)": 12e9, "Ka-band (20 GHz)": 20e9}
        frequency_value = freq_map[frequency]
        
        # Ground station parameters
        st.subheader("Ground Station Parameters")
        ground_antenna_gain = st.slider("Ground Antenna Gain (dBi)", 30.0, 60.0, 45.0, 1.0)
        ground_noise_temp = st.slider("Ground Noise Temperature (K)", 100.0, 500.0, 290.0, 10.0)
        ground_system_losses = st.slider("System Losses (dB)", 0.0, 5.0, 2.0, 0.1)
        
        # Path parameters
        st.subheader("Path Parameters")
        distance = st.selectbox("Satellite Altitude", ["LEO (500 km)", "MEO (10,000 km)", "GEO (35,786 km)"])
        dist_map = {"LEO (500 km)": 500e3, "MEO (10,000 km)": 10000e3, "GEO (35,786 km)": 35786e3}
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

    # Initialize configuration
    config = Config()
    config.SATELLITE_POWER = sat_power
    config.SATELLITE_ANTENNA_GAIN = sat_antenna_gain
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
            visualizer = Visualizer()
            
            if config.FEC_TYPE == "Repetition":
                fec = ErrorCorrection(coding_rate=config.CODING_RATE)
            else:
                fec = ErrorCorrection(coding_rate=1.0)
            
            # Calculate link budget
            st.markdown('<div class="sub-header">Link Budget Analysis</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("EIRP", f"{link_budget.calculate_eirp():.2f} dBW")
            with col2: st.metric("Path Loss", f"{link_budget.calculate_free_space_loss():.2f} dB")
            with col3: st.metric("Received Power", f"{link_budget.calculate_received_power():.2f} dBW")
            with col4: st.metric("C/N₀", f"{link_budget.calculate_cn0():.2f} dB-Hz")
            
            col5, col6, col7, col8 = st.columns(4)
            with col5: st.metric("Eb/N₀", f"{link_budget.calculate_ebn0():.2f} dB")
            with col6: 
                required_ebn0 = 9.6 if config.MODULATION_SCHEME == "QPSK" else 12.0
                margin = link_budget.calculate_link_margin(required_ebn0)
                st.metric("Link Margin", f"{margin:.2f} dB")
            
            # Link budget visualization
            link_params = {
                'EIRP': link_budget.calculate_eirp(),
                'Path Loss': -link_budget.calculate_free_space_loss(),
                'Rx Power': link_budget.calculate_received_power(),
                'C/N₀': link_budget.calculate_cn0(),
                'Eb/N₀': link_budget.calculate_ebn0()
            }
            
            st.markdown("### Link Budget Components")
            budget_img = visualizer.plot_link_budget(link_params)
            display_image_from_base64(budget_img)
            
            # Communication chain simulation
            st.markdown('<div class="sub-header">Communication Chain Simulation</div>', unsafe_allow_html=True)
            
            # Generate test data
            data_bits = np.random.randint(0, 2, config.NUM_BITS)
            encoded_bits = fec.encode(data_bits)
            symbols = modulator.modulate(encoded_bits)
            received_symbols = channel.simulate_channel(symbols)
            received_bits = modulator.demodulate(received_symbols)
            decoded_bits = fec.decode(received_bits[:len(encoded_bits)])
            ber = fec.calculate_ber(data_bits, decoded_bits)
            
            col9, col10, col11 = st.columns(3)
            with col9: st.metric("Original Bits", config.NUM_BITS)
            with col10: st.metric("Bit Errors", np.sum(data_bits != decoded_bits))
            with col11: st.metric("Bit Error Rate", f"{ber:.6f}")
            
            # Constellation diagram
            st.markdown("### Constellation Diagram")
            constellation_img = visualizer.plot_comparison_constellation(symbols[:200], received_symbols[:200])
            display_image_from_base64(constellation_img)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.info("👈 Adjust parameters and click 'Run Simulation' to start")

if __name__ == "__main__":
    main()