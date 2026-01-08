"""finetech NFT — Streamlit UI frontend for XRPL testnet interactions."""

import streamlit as st
import xrpl
import json
import xrpl_utils
import binascii
from xrpl.utils import str_to_hex
from xrpl_utils import mint_token, upload_to_ipfs  
from xrpl.models.requests import AccountTx
from config import APP_TITLE

# --- Configuration ---
st.set_page_config(page_title=APP_TITLE, layout="wide")

# Strict standard media types
ALLOWED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif")

@st.cache_resource
def get_xrpl_client():
    return xrpl_utils.connect_xrpl()

def _mask(val: str) -> str:
    if not val: return "N/A"
    return val if len(val) <= 8 else f"{val[:4]}...{val[-4:]}"

def decode_hex_uri(hex_str):
    if not hex_str: return None
    try:
        decoded_str = binascii.unhexlify(hex_str).decode('utf-8')
        data = json.loads(decoded_str)
        img_val = data.get("i") or data.get("im")
        if img_val and img_val.startswith("ipfs://"):
            return img_val.replace("ipfs://", "https://gateway.pinata.cloud/ipfs/")
        return img_val
    except Exception:
        return None

def main():
    st.title(f"🖼️ {APP_TITLE}")
    client = get_xrpl_client()

    if "wallet" not in st.session_state: st.session_state.wallet = None

    # --- Section 1: Wallet Connection ---
    if st.session_state.wallet is None:
        st.header("Connect to Testnet")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🆕 Generate New Wallet", use_container_width=True):
                st.session_state.wallet = xrpl_utils.generate_test_wallet(client)
                st.rerun()
        with c2:
            seed = st.text_input("Import Seed", type="password")
            if seed and st.button("📥 Import Wallet", use_container_width=True):
                try:
                    st.session_state.wallet = xrpl.wallet.Wallet.from_seed(seed)
                    st.rerun()
                except Exception as e: st.error(f"Invalid seed: {e}")
        return

    wallet = st.session_state.wallet

    # --- Tabs ---
    tab_mint, tab_gallery, tab_history = st.tabs(["🚀 Bulk Mint", "🎨 My Gallery", "📜 History"])

    with tab_mint:
        st.header("📦 Secure Atomic Batch Minting")
        files = st.file_uploader(
            "Upload Assets (Images & GIFs only)", 
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg", "gif"]
        )
        
        if files:
            taxon = st.number_input("Taxon ID", value=100)
            royalty_pct = st.slider("Royalty %", 0.0, 50.0, 5.0)
            st.info(f"Ready to mint {len(files)} items. Total failures will halt the batch.")

            if st.button(f"🔥 Start Atomic Minting", type="primary"):
                progress_bar = st.progress(0)
                status = st.empty()
                
                for i, file in enumerate(files):
                    if not file.name.lower().endswith(ALLOWED_EXTENSIONS):
                        st.error(f"❌ REJECTED: '{file.name}' is not an image.")
                        st.stop() 

                    # Step 1: IPFS Upload
                    status.text(f"Step 1/3: Uploading {file.name} to IPFS...")
                    try:
                        cid = upload_to_ipfs(file.getvalue(), file.name)
                    except Exception as e:
                        st.error(f"❌ IPFS FAILURE: {e}")
                        st.stop() 
                    
                    # Step 2: Metadata (Hex encoded)
                    status.text(f"Step 2/3: Creating Metadata for {file.name}...")
                    metadata = {"n": file.name[:20], "i": f"ipfs://{cid}"}
                    uri_hex = str_to_hex(json.dumps(metadata))
                    
                    if len(uri_hex) > 512:
                        st.error(f"❌ LIMIT: Metadata too long for {file.name}.")
                        st.stop()

                    # Step 3: XRPL Minting
                    status.text(f"Step 3/3: Finalizing on XRP Ledger...")
                    result = mint_token(wallet.seed, uri_hex, taxon=int(taxon), transfer_fee=int(royalty_pct*100))
                    
                    res_status = ""
                    if isinstance(result, dict):
                        res_status = result.get("engine_result") or result.get("meta", {}).get("TransactionResult")
                    
                    if res_status != "tesSUCCESS":
                        st.error(f"❌ LEDGER ERROR on {file.name}: {res_status}")
                        st.stop()
                    
                    progress_bar.progress((i + 1) / len(files))
                
                status.text("✅ Success! All NFTs are now on the Ledger.")
                st.balloons()

    with tab_gallery:
        if st.button("🔄 Refresh My Collection"):
            with st.spinner("Fetching NFTs..."):
                data = xrpl_utils.get_tokens(wallet.classic_address)
                nfts = data.get("account_nfts", [])
                if not nfts: st.info("No NFTs found.")
                else:
                    cols = st.columns(3)
                    for idx, nft in enumerate(nfts):
                        with cols[idx % 3]:
                            img_url = decode_hex_uri(nft.get("URI"))
                            if img_url: st.image(img_url, use_container_width=True)
                            st.write(f"**ID:** `{_mask(nft.get('NFTokenID'))}`")

    with tab_history:
        st.header("📜 Ledger Activity")
        if st.button("🔍 Fetch Recent Transactions"):
            response = client.request(AccountTx(account=wallet.classic_address, limit=10))
            tx_list = response.result.get("transactions", [])
            
            if not tx_list:
                st.info("No transactions found.")
            
            for tx_entry in tx_list:
                # DEEP SEARCH: Look into common wrapping keys used by different nodes/libraries
                tx_data = tx_entry.get("tx") or tx_entry.get("tx_json") or tx_entry
                meta_data = tx_entry.get("meta") or tx_entry.get("meta_data") or {}
                
                # Extract Type and Result with proper key names
                t_type = tx_data.get("TransactionType") or tx_data.get("transaction_type")
                t_res = meta_data.get("TransactionResult") or tx_entry.get("engine_result")
                
                # Format for display
                display_type = str(t_type) if t_type else "Unknown Transaction"
                display_res = str(t_res) if t_res else "tesSUCCESS"

                # UI Styling
                icon = "💎"
                if t_type == "NFTokenMint": icon = "🚀"
                elif t_type == "Payment": icon = "💰"
                elif t_type == "AccountSet": icon = "⚙️"

                with st.expander(f"{icon} {display_type} | {display_res}"):
                    st.json(tx_entry)

if __name__ == "__main__":
    main()