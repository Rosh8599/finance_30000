import psycopg2
import streamlit as st
import datetime

# Database connection function
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="finance portfolio",
            user="postgres",
            password="Rosh@8599"
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"Error: Unable to connect to the database. {e}")
        return None

# CRUD Functions
# Create
def add_user(username, email):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (username, email) VALUES (%s, %s) RETURNING user_id;", (username, email))
                conn.commit()
                return cur.fetchone()[0]
        except (psycopg2.IntegrityError, psycopg2.OperationalError) as e:
            st.error(f"Error adding user: {e}")
            return None

def add_account(user_id, account_name, account_type):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO accounts (user_id, account_name, account_type) VALUES (%s, %s, %s) RETURNING account_id;",
                            (user_id, account_name, account_type))
                conn.commit()
                return cur.fetchone()[0]
        except (psycopg2.IntegrityError, psycopg2.OperationalError) as e:
            st.error(f"Error adding account: {e}")
            return None

def add_asset(account_id, ticker, asset_name, asset_class):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO assets (account_id, ticker_symbol, asset_name, asset_class) VALUES (%s, %s, %s, %s) RETURNING asset_id;",
                            (account_id, ticker, asset_name, asset_class))
                conn.commit()
                return cur.fetchone()[0]
        except (psycopg2.IntegrityError, psycopg2.OperationalError) as e:
            st.error(f"Error adding asset: {e}")
            return None

def add_transaction(asset_id, transaction_type, date, quantity, price, total_amount):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO transactions (asset_id, transaction_type, transaction_date, quantity, price_per_unit, total_amount)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING transaction_id;
                """, (asset_id, transaction_type, date, quantity, price, total_amount))
                conn.commit()
                return cur.fetchone()[0]
        except (psycopg2.IntegrityError, psycopg2.OperationalError) as e:
            st.error(f"Error adding transaction: {e}")
            return None

# Read
def get_user_data(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
            return cur.fetchone()

def get_accounts_by_user(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM accounts WHERE user_id = %s;", (user_id,))
            return cur.fetchall()

def get_assets_by_account(account_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM assets WHERE account_id = %s;", (account_id,))
            return cur.fetchall()

def get_transactions_by_asset(asset_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM transactions WHERE asset_id = %s ORDER BY transaction_date DESC;", (asset_id,))
            return cur.fetchall()

# Update
def update_user_email(user_id, new_email):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET email = %s WHERE user_id = %s;", (new_email, user_id))
                conn.commit()
                return True
        except (psycopg2.IntegrityError, psycopg2.OperationalError) as e:
            st.error(f"Error updating user email: {e}")
            return False

# Delete
def delete_account(account_id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Delete related transactions first due to foreign key constraints
                cur.execute("DELETE FROM transactions WHERE asset_id IN (SELECT asset_id FROM assets WHERE account_id = %s);", (account_id,))
                cur.execute("DELETE FROM assets WHERE account_id = %s;", (account_id,))
                cur.execute("DELETE FROM accounts WHERE account_id = %s;", (account_id,))
                conn.commit()
                return True
        except (psycopg2.IntegrityError, psycopg2.OperationalError) as e:
            st.error(f"Error deleting account: {e}")
            return False

# Business Insights Functions
def get_asset_class_breakdown(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.asset_class, SUM(t.total_amount) as total_value
                FROM users u
                JOIN accounts acc ON u.user_id = acc.user_id
                JOIN assets a ON acc.account_id = a.account_id
                JOIN transactions t ON a.asset_id = t.asset_id
                WHERE u.user_id = %s AND t.transaction_type = 'buy'
                GROUP BY a.asset_class
                ORDER BY total_value DESC;
            """, (user_id,))
            return cur.fetchall()

def get_portfolio_summary_by_asset(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    a.ticker_symbol,
                    SUM(CASE WHEN t.transaction_type = 'buy' THEN t.quantity ELSE -t.quantity END) AS total_quantity,
                    SUM(CASE WHEN t.transaction_type = 'buy' THEN t.total_amount ELSE -t.total_amount END) AS total_cost_basis
                FROM users u
                JOIN accounts acc ON u.user_id = acc.user_id
                JOIN assets a ON acc.account_id = a.account_id
                JOIN transactions t ON a.asset_id = t.asset_id
                WHERE u.user_id = %s
                GROUP BY a.ticker_symbol
                HAVING SUM(CASE WHEN t.transaction_type = 'buy' THEN t.quantity ELSE -t.quantity END) > 0;
            """, (user_id,))
            return cur.fetchall()

def get_portfolio_metrics(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(DISTINCT a.ticker_symbol) AS num_assets,
                    SUM(t.total_amount) AS total_investment,
                    AVG(t.price_per_unit) AS avg_purchase_price,
                    MIN(t.transaction_date) AS first_transaction,
                    MAX(t.transaction_date) AS latest_transaction
                FROM users u
                JOIN accounts acc ON u.user_id = acc.user_id
                JOIN assets a ON acc.account_id = a.account_id
                JOIN transactions t ON a.asset_id = t.asset_id
                WHERE u.user_id = %s AND t.transaction_type = 'buy';
            """, (user_id,))
            return cur.fetchone()