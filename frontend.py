import streamlit as st
import pandas as pd
import backend as db
import datetime

st.set_page_config(layout="wide")
st.title("Financial Portfolio Tracker 💰")

# Assuming a single user for this application
# In a real-world app, you'd handle user authentication
USER_ID = 1

# If the user doesn't exist, create a new one
if not db.get_user_data(USER_ID):
    db.add_user("JohnDoe", "john.doe@example.com")

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Select a page", ["Dashboard", "Asset Management", "Transactions", "Business Insights"])

# Page: Dashboard
if page == "Dashboard":
    st.header("Dashboard Overview")
    st.info("This section provides a summary of your portfolio. (Note: Real-time values require an API call, not implemented in this database-focused example)")

    # Display portfolio summary (total cost basis)
    summary_data = db.get_portfolio_summary_by_asset(USER_ID)
    if summary_data:
        df_summary = pd.DataFrame(summary_data, columns=["Ticker", "Total Quantity", "Cost Basis"])
        total_cost_basis = df_summary["Cost Basis"].sum()
        st.metric(label="Total Portfolio Value (Cost Basis)", value=f"${total_cost_basis:,.2f}")
        st.subheader("Holdings by Ticker")
        st.dataframe(df_summary)
    else:
        st.warning("No assets found in your portfolio.")

# Page: Asset Management
elif page == "Asset Management":
    st.header("Asset & Account Management")

    accounts = db.get_accounts_by_user(USER_ID)
    account_names = {acc[0]: acc[2] for acc in accounts} if accounts else {}

    # Add Account Form
    with st.expander("➕ Add New Account"):
        with st.form("add_account_form"):
            account_name = st.text_input("Account Name", placeholder="e.g., Vanguard Brokerage")
            account_type = st.selectbox("Account Type", ["Brokerage", "Retirement", "Crypto Exchange"])
            submitted = st.form_submit_button("Add Account")
            if submitted and account_name:
                db.add_account(USER_ID, account_name, account_type)
                st.success(f"Account '{account_name}' added successfully!")
                st.experimental_rerun()

    # View and Add Assets
    if accounts:
        selected_account_id = st.selectbox("Select Account", options=list(account_names.keys()), format_func=lambda x: account_names[x])

        with st.expander("➕ Add New Asset to this Account"):
            with st.form("add_asset_form"):
                ticker = st.text_input("Ticker Symbol", placeholder="e.g., AAPL").upper()
                asset_name = st.text_input("Asset Name", placeholder="e.g., Apple Inc.")
                asset_class = st.selectbox("Asset Class", ["Equities", "Fixed Income", "Crypto", "Other"])
                submitted = st.form_submit_button("Add Asset")
                if submitted and ticker and asset_name:
                    db.add_asset(selected_account_id, ticker, asset_name, asset_class)
                    st.success(f"Asset '{ticker}' added to account!")
                    st.experimental_rerun()

        st.subheader("Assets in Selected Account")
        assets = db.get_assets_by_account(selected_account_id)
        if assets:
            df_assets = pd.DataFrame(assets, columns=["Asset ID", "Account ID", "Ticker", "Name", "Class"])
            st.dataframe(df_assets)
        else:
            st.info("No assets in this account yet.")

# Page: Transactions
elif page == "Transactions":
    st.header("Transaction Log")
    
    accounts = db.get_accounts_by_user(USER_ID)
    account_names = {acc[0]: acc[2] for acc in accounts} if accounts else {}
    
    if accounts:
        selected_account_id = st.selectbox("Select Account", options=list(account_names.keys()), format_func=lambda x: account_names[x])
        assets = db.get_assets_by_account(selected_account_id)
        asset_names = {a[0]: a[2] for a in assets} if assets else {}
        
        if assets:
            selected_asset_id = st.selectbox("Select Asset", options=list(asset_names.keys()), format_func=lambda x: asset_names[x])

            with st.expander("➕ Log New Transaction"):
                with st.form("log_transaction_form"):
                    transaction_type = st.radio("Transaction Type", ["Buy", "Sell", "Dividend"])
                    transaction_date = st.date_input("Date", datetime.date.today())
                    quantity = st.number_input("Quantity", min_value=0.01, format="%.2f")
                    price_per_unit = st.number_input("Price per Unit ($)", min_value=0.01, format="%.2f")
                    total_amount = quantity * price_per_unit
                    
                    submitted = st.form_submit_button("Log Transaction")
                    if submitted:
                        db.add_transaction(selected_asset_id, transaction_type.lower(), transaction_date, quantity, price_per_unit, total_amount)
                        st.success(f"{transaction_type} transaction logged for {asset_names[selected_asset_id]}.")
                        st.experimental_rerun()
            
            st.subheader("Transaction History")
            transactions = db.get_transactions_by_asset(selected_asset_id)
            if transactions:
                df_transactions = pd.DataFrame(transactions, columns=["ID", "Asset ID", "Type", "Date", "Quantity", "Price", "Amount"])
                st.dataframe(df_transactions)
            else:
                st.info("No transactions logged for this asset.")
        else:
            st.warning("Please add an asset to the selected account first.")
    else:
        st.warning("Please add an account first.")

# Page: Business Insights
elif page == "Business Insights":
    st.header("Portfolio Insights & Analytics 📈")

    col1, col2, col3 = st.columns(3)

    # Metrics section (COUNT, SUM, AVG, MIN, MAX)
    metrics = db.get_portfolio_metrics(USER_ID)
    if metrics:
        num_assets, total_investment, avg_purchase_price, first_tx, latest_tx = metrics
        
        with col1:
            st.metric("Total Assets", value=f"{num_assets} Tickers")
            st.metric("Total Investment", value=f"${total_investment:,.2f}")
        with col2:
            st.metric("Avg. Purchase Price", value=f"${avg_purchase_price:,.2f}")
        with col3:
            st.metric("First Transaction", value=first_tx.strftime("%Y-%m-%d") if first_tx else "N/A")
            st.metric("Latest Transaction", value=latest_tx.strftime("%Y-%m-%d") if latest_tx else "N/A")
    else:
        st.info("No data available for insights. Please add transactions.")

    st.markdown("---")
    
    # Asset Class Breakdown (pie chart)
    st.subheader("Portfolio Breakdown by Asset Class")
    breakdown_data = db.get_asset_class_breakdown(USER_ID)
    if breakdown_data:
        df_breakdown = pd.DataFrame(breakdown_data, columns=["Asset Class", "Total Value"])
        st.dataframe(df_breakdown)
        st.bar_chart(df_breakdown, x="Asset Class", y="Total Value")
    else:
        st.info("No asset class data to display. Please log transactions.")