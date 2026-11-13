-- Initial schema for Rozochka MVP
-- WARNING: intentionally simple, not production-hardened

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(64) UNIQUE,
    full_name VARCHAR(255),
    birth_date DATE,
    segment VARCHAR(64),
    has_savings_account BOOLEAN DEFAULT FALSE,
    active_deposits_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    account_type VARCHAR(64) NOT NULL,
    balance NUMERIC(18, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'RUB',
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    account_id INT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    amount NUMERIC(18, 2) NOT NULL,
    direction VARCHAR(8) NOT NULL CHECK (direction IN ('debit', 'credit')),
    category VARCHAR(128),
    merchant VARCHAR(255),
    description TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_events (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    event_type VARCHAR(128) NOT NULL,
    payload JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL,
    description TEXT,
    annual_rate NUMERIC(5, 2),
    min_amount NUMERIC(18, 2),
    max_amount NUMERIC(18, 2),
    term_months INT
);

CREATE TABLE IF NOT EXISTS offers (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id),
    trigger_type VARCHAR(128) NOT NULL,
    trigger_payload JSONB,
    message_text TEXT,
    status VARCHAR(32) DEFAULT 'pending' CHECK (status IN ('pending', 'shown', 'accepted', 'declined')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shown_at TIMESTAMP,
    responded_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_account_executed ON transactions(account_id, executed_at);
CREATE INDEX IF NOT EXISTS idx_app_events_client_created ON app_events(client_id, created_at);
CREATE INDEX IF NOT EXISTS idx_offers_client_status ON offers(client_id, status);
