CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    account_id INT NOT NULL,
    ticker_symbol VARCHAR(10) NOT NULL,
    asset_name VARCHAR(100),
    asset_class VARCHAR(50),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    asset_id INT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL, -- 'buy', 'sell', 'dividend'
    transaction_date DATE NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    price_per_unit DECIMAL(18, 8),
    total_amount DECIMAL(18, 2),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);