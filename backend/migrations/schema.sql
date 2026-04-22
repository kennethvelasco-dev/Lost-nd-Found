-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    admin_id TEXT,
    
    -- Verification
    is_email_verified BOOLEAN DEFAULT FALSE,
    verification_token TEXT,
    verification_token_expires TIMESTAMP WITH TIME ZONE,
    
    -- Security / Lockout
    failed_login_attempts INTEGER DEFAULT 0,
    lockout_until TIMESTAMP WITH TIME ZONE,
    
    -- Password Reset
    reset_token TEXT,
    reset_token_expires TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Lost Items Table
CREATE TABLE IF NOT EXISTS lost_items (
    id SERIAL PRIMARY KEY,
    report_id TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    item_type TEXT NOT NULL,
    color TEXT,
    brand TEXT,
    last_seen_location TEXT NOT NULL,
    last_seen_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    date_to_claim TIMESTAMP WITH TIME ZONE,
    public_description TEXT,
    private_details TEXT NOT NULL,
    main_picture TEXT,
    additional_picture_1 TEXT,
    additional_picture_2 TEXT,
    additional_picture_3 TEXT,
    reporter_id INTEGER NOT NULL REFERENCES users(id),
    claim_id INTEGER,
    processed_id TEXT,
    score_breakdown TEXT,
    status TEXT DEFAULT 'pending_approval',
    rejection_reason TEXT,
    recipient_name TEXT,
    recipient_id INTEGER,
    resolved_at TIMESTAMP WITH TIME ZONE,
    turnover_proof TEXT,
    is_dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lost_items_status ON lost_items(status);
CREATE INDEX IF NOT EXISTS idx_lost_items_category_type ON lost_items(category, item_type);
CREATE INDEX IF NOT EXISTS idx_lost_items_reporter ON lost_items(reporter_id);

-- Found Items Table
CREATE TABLE IF NOT EXISTS found_items (
    id SERIAL PRIMARY KEY,
    report_id TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    item_type TEXT NOT NULL,
    color TEXT,
    brand TEXT,
    found_location TEXT NOT NULL,
    found_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    date_to_claim TIMESTAMP WITH TIME ZONE,
    public_description TEXT,
    private_details TEXT,
    main_picture TEXT,
    additional_picture_1 TEXT,
    additional_picture_2 TEXT,
    additional_picture_3 TEXT,
    reporter_id INTEGER REFERENCES users(id),
    claim_id INTEGER,
    processed_id TEXT,
    status TEXT NOT NULL DEFAULT 'found',
    recipient_name TEXT,
    recipient_id INTEGER,
    resolved_at TIMESTAMP WITH TIME ZONE,
    turnover_proof TEXT,
    is_dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_found_items_status ON found_items(status);
CREATE INDEX IF NOT EXISTS idx_found_items_category_type ON found_items(category, item_type);
CREATE INDEX IF NOT EXISTS idx_found_items_reporter ON found_items(reporter_id);

-- Claims Table
CREATE TABLE IF NOT EXISTS claims (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    found_item_id INTEGER REFERENCES found_items(id),
    lost_item_id INTEGER REFERENCES lost_items(id),
    claimant_name TEXT NOT NULL,
    claimant_email TEXT NOT NULL,
    lost_location TEXT,
    lost_datetime TIMESTAMP WITH TIME ZONE,
    answers TEXT NOT NULL,
    verification_score INTEGER NOT NULL,
    decision TEXT NOT NULL DEFAULT 'pending',
    decision_reason TEXT,
    score_breakdown TEXT,
    pickup_datetime TIMESTAMP WITH TIME ZONE,
    pickup_location TEXT,
    handover_notes TEXT,
    completed_at TIMESTAMP WITH TIME ZONE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_claims_user ON claims(user_id);
CREATE INDEX IF NOT EXISTS idx_claims_item ON claims(found_item_id);
CREATE INDEX IF NOT EXISTS idx_claims_lost_item ON claims(lost_item_id);
CREATE INDEX IF NOT EXISTS idx_claims_decision ON claims(decision);

-- Activity Logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    performed_by TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Token Blocklist
CREATE TABLE IF NOT EXISTS token_blocklist (
    id SERIAL PRIMARY KEY,
    jti TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_token_blocklist_jti ON token_blocklist(jti);

-- Released Items Table (Historical records of resolved items)
CREATE TABLE IF NOT EXISTS released_items (
    id SERIAL PRIMARY KEY,
    original_report_id TEXT NOT NULL,
    item_source TEXT NOT NULL, -- 'lost' or 'found'
    category TEXT NOT NULL,
    item_type TEXT NOT NULL,
    claimant_name TEXT NOT NULL,
    recipient_id TEXT, -- Student/Staff ID
    released_by_admin TEXT NOT NULL,
    handover_notes TEXT,
    turnover_proof TEXT, -- Base64 or path

    -- Snapshot fields from original item
    color TEXT,
    brand TEXT,
    main_picture TEXT,
    public_description TEXT,
    last_seen_location TEXT,
    found_location TEXT,

    resolved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_released_items_report_id ON released_items(original_report_id);
CREATE INDEX IF NOT EXISTS idx_released_items_claimant ON released_items(claimant_name);

