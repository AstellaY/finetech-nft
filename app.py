"""finetech NFT — Streamlit UI frontend for XRPL testnet interactions."""

import streamlit as st
import xrpl
import json
import xrpl_utils
from xrpl.utils import str_to_hex
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

@st.cache_resource
def get_xrpl_client():
    return xrpl_utils.connect_xrpl()

def _mask(val: str) -> str:
    if not val:
        return "N/A"
    return val if len(val) <= 8 else f"{val[:4]}...{val[-4:]}"

def main():
    st.title(APP_TITLE)
    st.write(f"Welcome to {APP_SUBTITLE}")

    client = get_xrpl_client()
    st.success(MSG_CONNECTED)

    if "wallet" not in st.session_state:
        st.session_state.wallet = None

    # Section 1: Create / Import wallet
    st.header("Create / Access Testnet Wallet")
    col1, col2 = st.columns(2)

    if st.session_state.wallet is None:
        with col1:
            if st.button("🆕 Generate New Wallet", key="gen_wallet"):
                with st.spinner("Generating Wallet"):
                    wallet = xrpl_utils.generate_test_wallet(client)
                    st.session_state.wallet = wallet
                    st.rerun()

        with col2:
            seed_input = st.text_input("Or paste existing seed to import wallet")
            if seed_input and st.button("📥 Import Wallet", key="import_wallet"):
                try:
                    from xrpl.wallet import Wallet
                    wallet = Wallet.from_seed(seed_input)
                    st.session_state.wallet = wallet
                    st.rerun()
                except Exception as e:
                    st.error(f"Invalid seed: {e}")
        return

    # From here on, wallet exists
    wallet = st.session_state.wallet
    
    with st.expander("💼 Your Wallet Details", expanded=True):
        st.write(MSG_PUBLIC_KEY, _mask(getattr(wallet, "public_key", "")))
        st.write(MSG_PRIVATE_KEY, _mask(getattr(wallet, "private_key", "")))
        st.write(MSG_WALLET_ADDRESS, wallet.classic_address)
        st.write(MSG_WALLET_SEED, _mask(getattr(wallet, "seed", "")))
        
        # Account info button inside expander
        if st.button("View Account Balance & Info", key="view_account"):
            with st.spinner("Fetching account info"):
                acct_info = xrpl_utils.get_account_info(client, wallet.classic_address)
                if acct_info is None:
                    st.error(MSG_NO_ACCOUNT)
                else:
                    st.json(acct_info)

    # View NFTs
    if st.button("🖼️ View My Collection", key="view_nfts"):
        with st.spinner("Fetching NFTs..."):
            results = xrpl_utils.get_tokens(wallet.classic_address)
            nfts = results.get("account_nfts", []) if results else []
            if nfts:
                for nft in nfts:
                    with st.container(border=True):
                        uri_hex = nft.get("URI", "")
                        plain_uri = xrpl.utils.hex_to_str(uri_hex) if uri_hex else "N/A"
                        st.write(f"**NFT ID:** `{nft.get('NFTokenID')}`")
                        st.write(f"**URI:** {plain_uri}")
                        img = xrpl_utils.display_nft_image(uri_hex)
                        if img: st.image(img, width=200)
            else:
                st.info("No NFTs found.")

    st.markdown("---")

    # --- EDITED MULTIMEDIA PORTION ---
    st.header("🎨 Create Multimedia NFT")
    
    col_upload, col_meta = st.columns([1, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload Media",
            type=["mp3", "wav", "gif", "jpg", "jpeg", "png"],
        )
        if uploaded_file:
            if "audio" in uploaded_file.type:
                st.audio(uploaded_file)
            else:
                st.image(uploaded_file, caption="Preview", use_container_width=True)

    with col_meta:
        if uploaded_file:
            nft_name = st.text_input("Asset Name", value=uploaded_file.name)
            nft_desc = st.text_area("Description", placeholder="Describe this asset...")
            
            # Step 1: Prepare Metadata Object
            # In a real-life app, you'd upload the file to IPFS first.
            metadata = {
                "name": nft_name,
                "description": nft_desc,
                "image": f"ipfs://{uploaded_file.name}",
                "type": uploaded_file.type
            }
            
            st.caption("Metadata Preview (Standard XLS-20):")
            st.json(metadata)

            if st.button("🚀 Mint NFT", key="mint_multimedia", type="primary"):
                bal = xrpl_utils.get_account_balance(client, wallet.classic_address)
                if bal and bal >= 0.1:
                    with st.spinner("Encoding & Minting..."):
                        try:
                            # Step 2: Convert Metadata to HEX (Required by XRPL)
                            metadata_uri = str_to_hex(json.dumps(metadata))
                            
                            # Step 3: Submit Mint Transaction
                            result = mint_token(wallet.seed, metadata_uri, flags=8, enforce_single_owner=True)
                            
                            st.success(f"✅ '{nft_name}' minted successfully!")
                            tx_hash = result.get("hash") if isinstance(result, dict) else None
                            if tx_hash:
                                st.write(f"**Transaction:** [Explorer Link](https://test.bithomp.com/explorer/{tx_hash})")
                        except Exception as e:
                            st.error(f"❌ Minting failed: {e}")
                else:
                    st.error("Insufficient balance (0.1 XRP minimum).")

    if st.sidebar.button("Log Out", key="logout"):
        st.session_state.wallet = None
        st.rerun()

if __name__ == "__main__":
    main()