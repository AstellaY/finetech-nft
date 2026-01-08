"""analytics_engine.py — Fintech Logic & Audit Engine for Finetech NFT."""
import xrpl
import json
from xrpl.utils import str_to_hex

def get_portfolio_metrics(nfts, decode_func):
    """
    Performs a real-time audit of NFT data to generate professional metrics.
    """
    if not nfts:
        return None

    collections = {}
    for nft in nfts:
        # Get URI and decode it using the function passed from app.py
        img_url, col_name = decode_func(nft.get("URI"))
        if col_name not in collections:
            collections[col_name] = []
        
        collections[col_name].append({
            "img": img_url, 
            "id": nft.get("NFTokenID"),
            "taxon": nft.get("NFTokenTaxon")
        })

    # Business Intelligence Metrics
    stats = {
        "total_count": len(nfts),
        "collection_count": len(collections),
        "avg_collection_size": len(nfts) / len(collections) if collections else 0,
        "grouped_data": collections
    }
    return stats

def run_preflight_check(wallet_address, client, file_count):
    """
    Atomic Integrity Check: Ensures wallet has enough XRP for the batch.
    """
    from xrpl.models.requests import AccountInfo
    
    try:
        request = AccountInfo(account=wallet_address)
        response = client.request(request)
        
        # Balance is in drops (1 XRP = 1,000,000 drops)
        balance_drops = int(response.result['account_data']['Balance'])
        balance_xrp = balance_drops / 1_000_000
        
        # Estimate: 0.00001 per tx + standard owner reserve buffer
        # We estimate high to be safe
        required_xrp = file_count * 0.0002 
        
        if balance_xrp < required_xrp:
            return False, f"Insufficient XRP. Need ~{required_xrp} XRP, have {balance_xrp:.4f}"
            
        return True, "Pre-flight check passed."
    except Exception as e:
        return False, f"Account check failed: {str(e)}"