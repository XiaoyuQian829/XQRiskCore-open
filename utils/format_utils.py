def fmt_float(val, digits=2, suffix="", default="—"):
    if val is None:
        return default
    try:
        return f"{val:.{digits}f}{suffix}"
    except Exception:
        return default

def fmt_pct(val, digits=2, default="—"):
    if val is None:
        return default
    try:
        return f"{val:.{digits}%}"
    except Exception:
        return default

def fmt_money(val, digits=2, default="—"):
    if val is None:
        return default
    try:
        return f"${val:,.{digits}f}"
    except Exception:
        return default
