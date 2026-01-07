#UI streamlit frontend 
import streamlit as st
import xrpl_utils #blockchain logic

st.title("finetech NFT")
st.write("Welcome to finetech NFT")

#Calls function to connect to XRPL
client = xrpl_utils.connect_xrpl()  # Connect to XRPL testnet
st.write("Connected to XRPL testnet")  # Show connection

if st.button("Mint NFT"):
    st.write("Minting NFT...")
