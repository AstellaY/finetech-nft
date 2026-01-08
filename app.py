"""finetech NFT — Professional XRPL Suite with Smart Hooking & Asset Metrics."""

import streamlit as st
import xrpl
import json
import xrpl_utils
import analytics_engine  # <--- Ensure analytics_engine.py is in the same folder
import binascii
from xrpl.utils import str_to_hex
from xrpl_utils import mint_token, upload_to_ipfs  
from xrpl.models.requests import AccountTx
from config import APP_TITLE

# --- Configuration ---
st.set_page_config(page_title=APP_TITLE, layout="wide")

@st.cache_resource
def get_xrpl_client():
    return xrpl_utils.connect_xrpl()

def _mask(val: str) -> str:
    if not val: return "N/A"
    return val if len(val) <= 8 else f"{val[:4]}...{val[-4:]}"

def decode_hex_uri(hex_str):
    if not hex_str: return None, "Standard Collection"
    try:
        decoded_str = binascii.unhexlify(hex_str).decode('utf-8')
        data = json.loads(decoded_str)
        img_val = data.get("i") or data.get("im")
        img_url = img_val.replace("ipfs://", "https://gateway.pinata.cloud/ipfs/") if img_val and img_val.startswith("ipfs://") else img_val
        col_name = data.get("c") or "Standard Collection"
        return img_url, col_name
    except Exception: return None, "Standard Collection"

def main():
    st.title(f"🖼️ {APP_TITLE}")
    client = get_xrpl_client()

    if "wallet" not in st.session_state: 
        st.session_state.wallet = None

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
    tab_mint, tab_gallery, tab_history = st.tabs(["🚀 Smart Mint", "🎨 Asset Portfolio", "📜 History"])

    with tab_mint:
        st.header("📦 Collection Manager")
        with st.spinner("Syncing collection data..."):
            token_data = xrpl_utils.get_tokens(wallet.classic_address)
            nfts = token_data.get("account_nfts", [])
            collection_map = {decode_hex_uri(nft.get("URI"))[1]: nft.get("NFTokenTaxon") for nft in nfts}
        
        has_collections = len(collection_map) > 0
        col_a, col_b = st.columns(2)
        with col_a:
            mode = st.radio("Minting Mode", ["Create New", "Add to Existing"])
            if mode == "Add to Existing" and has_collections:
                target_name = st.selectbox("Hook to Collection", options=list(collection_map.keys()))
                target_taxon = collection_map[target_name]
            else:
                if mode == "Add to Existing": st.warning("⚠️ No collections found. Switching to 'New'.")
                target_name = st.text_input("New Collection Name", value="Genesis Drop")
                target_taxon = max(collection_map.values()) + 1 if collection_map else 100
        
        with col_b:
            royalty_pct = st.slider("Royalty %", 0.0, 50.0, 5.0)
            st.metric("Target Taxon ID", target_taxon if target_name else "N/A")

        files = st.file_uploader("Upload Assets", accept_multiple_files=True, type=["png", "jpg", "jpeg", "gif"])
        
        if files:
            if st.button(f"🔥 Launch Batch Mint", type="primary", use_container_width=True):
                # ATOMIC PRE-FLIGHT CHECK via our separate logic engine
                success, msg = analytics_engine.run_preflight_check(wallet.classic_address, client, len(files))
                if not success:
                    st.error(msg)
                else:
                    progress_bar = st.progress(0)
                    status = st.empty()
                    for i, file in enumerate(files):
                        status.text(f"Processing {file.name}...")
                        cid = upload_to_ipfs(file.getvalue(), file.name)
                        metadata = {"n": file.name[:20], "c": target_name, "i": f"ipfs://{cid}"}
                        mint_token(wallet.seed, str_to_hex(json.dumps(metadata)), taxon=int(target_taxon), transfer_fee=int(royalty_pct*100))
                        progress_bar.progress((i + 1) / len(files))
                    st.success(f"Batch Complete! '{target_name}' updated.")
                    st.balloons()
                    st.rerun()

    with tab_gallery:
        st.header("🎨 Professional Asset Portfolio")
        if st.button("🔄 Sync Portfolio Metrics", use_container_width=True):
            with st.spinner("Analyzing Ledger Assets..."):
                data = xrpl_utils.get_tokens(wallet.classic_address)
                nfts = data.get("account_nfts", [])
                stats = analytics_engine.get_portfolio_metrics(nfts, decode_hex_uri)
                
                if not stats:
                    st.info("No assets found.")
                else:
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Assets", stats["total_count"])
                    m2.metric("Unique Collections", stats["collection_count"])
                    m3.metric("Avg. Grouping", f"{stats['avg_collection_size']:.1f}")
                    st.divider()

                    for name, items in stats["grouped_data"].items():
                        with st.expander(f"📁 {name} ({len(items)} Items)", expanded=True):
                            cols = st.columns(4)
                            for idx, item in enumerate(items):
                                with cols[idx % 4]:
                                    if item["img"]: st.image(item["img"], use_container_width=True)
                                    st.caption(f"ID: `{_mask(item['id'])}`")

    with tab_history:
        st.header("📜 Ledger Audit Trail")
        if st.button("🔍 Sync Transactions", use_container_width=True):
            response = client.request(AccountTx(account=wallet.classic_address, limit=15))
            tx_list = response.result.get("transactions", [])
            
            if not tx_list:
                st.info("No history found.")

            for tx_entry in tx_list:
                # Deep Search Logic to prevent 'None' or 'Unknown' types
                tx_data = tx_entry.get("tx") or tx_entry.get("tx_json") or tx_entry
                meta_data = tx_entry.get("meta") or tx_entry.get("meta_data") or {}
                
                t_type = tx_data.get("TransactionType") or "Other"
                t_res = meta_data.get("TransactionResult") or "N/A"
                t_hash = tx_data.get("hash") or tx_entry.get("hash") or "N/A"
                t_fee = int(tx_data.get("Fee", 0)) / 1_000_000
                
                icon = "🚀" if t_type == "NFTokenMint" else "💰" if t_type == "Payment" else "⚙️"
                color = "green" if str(t_res) == "tesSUCCESS" else "red"
                
                with st.expander(f"{icon} {t_type} — :{color}[{t_res}]"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Network Fee", f"{t_fee} XRP")
                    c2.write(f"**Hash:** `{_mask(t_hash)}`")
                    if t_hash != "N/A":
                        explorer_url = f"https://testnet.xrpscan.com/tx/{t_hash}"
                        c3.link_button("🌐 XRPScan", explorer_url)
                    
                    st.divider()
                    st.json(tx_entry)

if __name__ == "__main__":
    main()