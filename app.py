"""finetech NFT — Streamlit UI frontend for XRPL testnet interactions."""

import streamlit as st
import xrpl_utils
from xrpl_utils import mint_token
from config import (
    APP_TITLE,
    APP_SUBTITLE,
    MSG_CONNECTED,
    MSG_PUBLIC_KEY,
    MSG_PRIVATE_KEY,
    MSG_WALLET_ADDRESS,
    MSG_WALLET_SEED,
    MSG_WALLET_BALANCE,
    MSG_NO_ACCOUNT,
    MSG_MINTING_FUTURE,
)

#decorator to cache the XRPL client connection (avoids redundant API calls on every re-run)
@st.cache_resource
def get_xrpl_client():
    """Get cached XRPL client to avoid redundant connections."""
    return xrpl_utils.connect_xrpl()


def main():
    """Main Streamlit app."""
    # Header
    st.title(APP_TITLE)
    st.write(f"Welcome to {APP_SUBTITLE}")

    # Connect to XRPL (cached)
    client = get_xrpl_client()
    st.success(MSG_CONNECTED)

    # Initialize session state for wallet
    if 'wallet' not in st.session_state:
        st.session_state.wallet = None
    
    # Section 1: Generate or Access Wallet
    st.header("Step 1: Create / Access Testnet Wallet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🆕 Generate New Wallet"):
            wallet = xrpl_utils.generate_test_wallet(client)
            st.session_state.wallet = wallet
            st.success("Wallet generated!")
    
    with col2:
        seed_input = st.text_input("Or paste existing seed to import wallet")
        if seed_input and st.button("📥 Import Wallet"):
            try:
                from xrpl.wallet import Wallet
                wallet = Wallet.from_seed(seed_input)
                st.session_state.wallet = wallet
                st.success("Wallet imported!")
            except Exception as e:
                st.error(f"Invalid seed: {e}")
    
    # Display wallet info if wallet is ready
    if st.session_state.wallet:
        st.markdown("---")
        st.subheader("💼 Your Wallet Details")
        
        wallet = st.session_state.wallet
        st.write(MSG_PUBLIC_KEY, wallet.public_key)
        st.write(MSG_PRIVATE_KEY, wallet.private_key)
        st.write(MSG_WALLET_ADDRESS, wallet.classic_address)
        st.write(MSG_WALLET_SEED, wallet.seed)
        
        bal = xrpl_utils.get_account_balance(client, wallet.classic_address)
        st.write(MSG_WALLET_BALANCE, bal)
        
        # Section 2: Check Balance (only shown if wallet exists)
        st.markdown("---")
        st.subheader("Step 2: Mint NFT")
        
        nft_uri = st.text_input("Enter NFT metadata URI", placeholder="https://example.com/nft-metadata.json")
        
        if st.button("🎨 Mint NFT"):
            if nft_uri:
                with st.spinner("Minting NFT... this may take a moment"):
                    try:
                        result = mint_token(wallet.seed, nft_uri)
                        st.success("✅ NFT minted successfully!")
                        st.write("**Transaction Result:**", result)
                    except Exception as e:
                        st.error(f"❌ Minting failed: {str(e)}")
            else:
                st.error("Please enter a metadata URI")
    else:
        # Show info message if wallet not ready
        st.info("👆 Please generate or import a wallet first to access minting features")
    
    st.markdown("---")
    st.caption("Never share your private key or seed with anyone!")


if __name__ == "__main__":
    main()


