-- Initial schema for next_offer MVP
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

CREATE TABLE IF NOT EXISTS banner_templates (
    id SERIAL PRIMARY KEY,
    type VARCHAR(64) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    subtitle TEXT,
    background_color VARCHAR(255),
    icon VARCHAR(255),
    action_text VARCHAR(64),
    product_id INT REFERENCES products(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS offers (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id),
    banner_template_id INT REFERENCES banner_templates(id),
    event_id VARCHAR(64) UNIQUE,
    trigger_type VARCHAR(128) NOT NULL,
    trigger_payload JSONB,
    message_text TEXT,
    status VARCHAR(32) DEFAULT 'pending' CHECK (status IN ('pending', 'shown', 'accepted', 'declined', 'dismissed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shown_at TIMESTAMP,
    responded_at TIMESTAMP
);

-- Additive migration for databases created before banner templates existed.
ALTER TABLE offers ADD COLUMN IF NOT EXISTS banner_template_id INT REFERENCES banner_templates(id);
ALTER TABLE offers ADD COLUMN IF NOT EXISTS event_id VARCHAR(64) UNIQUE;
ALTER TABLE offers DROP CONSTRAINT IF EXISTS offers_status_check;
ALTER TABLE offers ADD CONSTRAINT offers_status_check
    CHECK (status IN ('pending', 'shown', 'accepted', 'declined', 'dismissed'));

CREATE INDEX IF NOT EXISTS idx_transactions_account_executed ON transactions(account_id, executed_at);
CREATE INDEX IF NOT EXISTS idx_app_events_client_created ON app_events(client_id, created_at);
CREATE INDEX IF NOT EXISTS idx_offers_client_status ON offers(client_id, status);

-- Demo seed: one client, one account, one savings product and the salary banner.
INSERT INTO products (code, name, category, description, annual_rate, min_amount)
VALUES (
    'savings_account',
    'Накопительный счёт',
    'savings',
    'Счёт с ежемесячной капитализацией процентов',
    8.00,
    1000
)
ON CONFLICT (code) DO NOTHING;

INSERT INTO clients (external_id, full_name, segment, has_savings_account, active_deposits_count)
VALUES ('demo-client-1', 'Иван Петров', 'mass', FALSE, 0)
ON CONFLICT (external_id) DO NOTHING;

INSERT INTO accounts (client_id, account_type, balance, currency)
SELECT c.id, 'current', 150000.00, 'RUB'
FROM clients c
WHERE c.external_id = 'demo-client-1'
  AND NOT EXISTS (
      SELECT 1 FROM accounts a
      WHERE a.client_id = c.id AND a.account_type = 'current'
  );

INSERT INTO banner_templates (type, title, subtitle, background_color, icon, action_text, product_id)
VALUES (
    'salary',
    'Сохраните зарплату под 8%',
    'Отложите часть на накопительный счёт с ежемесячной капитализацией',
    'linear-gradient(135deg, #7c3aed 0%, #db2777 100%)',
    '💰',
    'Открыть счёт',
    (SELECT id FROM products WHERE code = 'savings_account')
)
ON CONFLICT (type) DO NOTHING;
