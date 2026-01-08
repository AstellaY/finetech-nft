import streamlit as st
import xrpl_utils

st.title("finetech NFT")
st.write("Welcome to finetech NFT — simple XRPL testnet demo")

client = xrpl_utils.connect_xrpl()
st.success("Connected to XRPL testnet")

st.header("Create / Inspect Testnet Wallet")

if st.button("Generate Testnet Wallet"):
    wallet = xrpl_utils.generate_test_wallet(client)
    st.write("**Classic Address:**", wallet.classic_address)
    st.write("**Seed (keep private):**", wallet.seed)
    bal = xrpl_utils.get_account_balance(client, wallet.classic_address)
    st.write("**Balance (XRP):**", bal)

st.markdown("---")

st.header("Check Balance for an Existing Address")
addr = st.text_input("Enter a classic address (r...) to check balance")
if addr:
    bal = xrpl_utils.get_account_balance(client, addr)
    if bal is None:
        st.error("Account not found or no balance")
    else:
        st.write("Balance (XRP):", bal)

st.markdown("\n\nMinting functionality is a future step — ask me to add it.")
