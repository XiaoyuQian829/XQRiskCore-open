# utils/rebalance_utils.py

def get_next_rebalance_schedule(asset_type):
    if asset_type == "stock":
        return "weekly"      
    elif asset_type == "etf":
        return "biweekly"    
    elif asset_type == "bond":
        return "monthly"     
    else:
        return "monthly"     
