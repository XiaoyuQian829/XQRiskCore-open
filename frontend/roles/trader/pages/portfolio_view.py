# frontend/roles/trader/pages/portfolio_view.py

REQUIRES_CLIENT_CONTEXT = True

import streamlit as st
import pandas as pd
import plotly.express as px
import io
from urllib.parse import quote

from core.request_context import RequestContext
from core.client_context import ClientContext

from audit.action_logger import record_user_view
from utils.user_action import UserAction


def render_account_summary(capital, total_invested, total_account_value):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Account Value", f"${total_account_value:,.2f}")
    col2.metric("Cash (Uninvested)", f"${capital:,.2f}")
    delta_pct = (total_invested / total_account_value * 100) if total_account_value > 0 else 0
    col3.metric("Total Invested", f"${total_invested:,.2f}", delta=f"{delta_pct:.2f}%")
    col4.markdown("&nbsp;", unsafe_allow_html=True)

def render_category_metrics(category_total_value, total_account_value):
    if not category_total_value:
        st.info("No category data available.")
        return
    sorted_items = sorted(category_total_value.items(), key=lambda x: x[1], reverse=True)
    cols = st.columns(min(len(sorted_items), 4))
    for i, (cat, val) in enumerate(sorted_items):
        pct = (val / total_account_value * 100) if total_account_value > 0 else 0
        cols[i % len(cols)].metric(cat, f"${val:,.2f}", delta=f"{pct:.2f}%")

def render_allocation_pie_chart(allocation_data):
    fig = px.pie(
        names=list(allocation_data.keys()),
        values=list(allocation_data.values()),
        title="Account Allocation Breakdown",
        hole=0.4
    )
    fig.update_traces(textinfo='label+percent', hoverinfo='label+value+percent')
    st.plotly_chart(fig, use_container_width=True)

def render_subcategory_pie_chart(holdings, category):
    if len(holdings) < 2:
        return
    fig = px.pie(
        names=[item["symbol"] for item in holdings],
        values=[item["value"] for item in holdings],
        title=f"Allocation within {category}",
        hole=0.35
    )
    fig.update_traces(textinfo='label+percent', hoverinfo='label+value+percent')
    st.plotly_chart(fig, use_container_width=True)

def render_holdings_table(holdings, portfolio_assets, category, capital):
    details = []
    total_unrealized_pnl = 0.0

    for asset in holdings:
        symbol = asset["symbol"]
        info = portfolio_assets[symbol]
        position = info.get("position", 0)
        price = info.get("current_price", 0.0)
        avg_price = info.get("avg_price", 0.0)
        value = position * price

        unrealized_pnl = (price - avg_price) * position if avg_price > 0 else 0.0
        pnl_pct = (unrealized_pnl / (avg_price * position)) * 100 if avg_price > 0 else 0.0
        total_unrealized_pnl += unrealized_pnl

        chart_url = f"/symbol_chart?symbol={quote(symbol)}&category={quote(category)}"
        view_button = f"[View Chart]({chart_url})"

        details.append({
            "Symbol": symbol,
            "Position": position,
            "Avg Entry Price": avg_price,
            "Current Price": price,
            "Market Value": value,
            "Unrealized PnL": unrealized_pnl,
            "PnL %": pnl_pct,
            "Chart": view_button
        })

    df = pd.DataFrame(details).sort_values(by="Unrealized PnL", ascending=False)

    def style_pnl(val):
        return "color: red;" if val < 0 else "color: green;"

    styled_df = df.style.format({
        "Avg Entry Price": "${:,.2f}",
        "Current Price": "${:,.2f}",
        "Market Value": "${:,.2f}",
        "Unrealized PnL": "${:,.2f}",
        "PnL %": "{:.2f}%"
    }).applymap(style_pnl, subset=["Unrealized PnL", "PnL %"])

    st.markdown(f"<h4 style='margin-top: 1rem;'>Holdings in {category}</h4>", unsafe_allow_html=True)
    st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)

    pnl_color = "green" if total_unrealized_pnl >= 0 else "red"
    st.markdown(
        f"<b>Total Unrealized PnL:</b> <span style='color:{pnl_color}'>${total_unrealized_pnl:,.2f}</span>",
        unsafe_allow_html=True
    )

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download Holdings as CSV",
        data=csv_buffer.getvalue(),
        file_name=f"{category.lower()}_holdings.csv",
        mime="text/csv"
    )


def render(ctx: RequestContext, client: ClientContext):

    st.markdown(f"""
    <div style='padding: 0.6rem 1rem; background-color: rgba(255,255,255,0.05); border-left: 4px solid #4dabf7; margin-bottom: 1rem; font-size: 0.95rem; color: #eee;'>
        📌 <strong style="color: #ccc;">Active Client:</strong> <code style="background-color: rgba(255,255,255,0.08); color: #00e676;">{client.client_id}</code>
    </div>
    """, unsafe_allow_html=True)

    if not ctx.has_permission("trader.view_portfolio"):
        st.error("🚫 Access denied: you lack permission `trader.view_portfolio`")
        return


    record_user_view(ctx, module="portfolio_view", action=UserAction.VIEW_PORTFOLIO)

    st.markdown("<h3 style='font-size: 1.7rem; margin-bottom: 0.5rem;'>Portfolio Overview</h3>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    portfolio_assets = client.portfolio_state.get("assets", {})
    capital = client.portfolio_state.get("capital", 0.0)

    if not portfolio_assets:
        st.warning("No holdings found. All positions may have been closed, or trading is currently restricted.")
        return

    symbol_to_category = client.config_loader.symbol_category_map
    categorized_assets = {}
    category_total_value = {}

    for symbol, info in portfolio_assets.items():
        pos = info.get("position", 0)
        price = info.get("current_price", 0.0)
        if pos <= 0 or price <= 0:
            continue

        value = pos * price
        category = symbol_to_category.get(symbol.upper(), "Uncategorized")
        categorized_assets.setdefault(category, []).append({"symbol": symbol, "value": value})
        category_total_value[category] = category_total_value.get(category, 0.0) + value

    total_invested = sum(category_total_value.values())
    total_account_value = capital + total_invested

    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 0.5rem;'>Account Summary</h3>", unsafe_allow_html=True)
    render_account_summary(capital, total_invested, total_account_value)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 0.5rem;'>Allocation by Category</h3>", unsafe_allow_html=True)
    allocation_data = {"Cash": capital, **category_total_value}
    render_category_metrics(category_total_value, total_account_value)
    render_allocation_pie_chart(allocation_data)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 0.5rem;'>Category Details</h3>", unsafe_allow_html=True)
    selected_category = st.radio("Select a category to inspect:", options=list(allocation_data.keys()), index=0)


    record_user_view(ctx, module="portfolio_view", action="view_category", payload={"category": selected_category})

    if selected_category == "Cash":
        st.info(f"Cash reserve of ${capital:,.2f} is currently unallocated.")
        return

    holdings = categorized_assets.get(selected_category, [])
    if not holdings:
        st.warning(f"No active holdings in '{selected_category}'.")
        return

    render_subcategory_pie_chart(holdings, selected_category)
    render_holdings_table(holdings, portfolio_assets, selected_category, capital)



