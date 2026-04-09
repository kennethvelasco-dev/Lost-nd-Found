CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'admin')),
    email TEXT UNIQUE,
    name TEXT,
    admin_id TEXT,
    is_email_verified INTEGER DEFAULT 0,
    verification_token TEXT,
    verification_token_expires TEXT,
    reset_token TEXT,
    reset_token_expires TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE TABLE IF NOT EXISTS lost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    item_type TEXT NOT NULL,
    color TEXT,
    brand TEXT,
    last_seen_location TEXT NOT NULL,
    last_seen_datetime TEXT NOT NULL,
    date_to_claim TEXT,
    public_description TEXT,
    private_details TEXT NOT NULL,
    main_picture TEXT,
    additional_picture_1 TEXT,
    additional_picture_2 TEXT,
    additional_picture_3 TEXT,
    reporter_id INTEGER NOT NULL,
    claim_id INTEGER,
    processed_id TEXT,
    score_breakdown TEXT,
    status TEXT DEFAULT 'pending_approval',
    rejection_reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (reporter_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_lost_items_status ON lost_items(status);
CREATE INDEX IF NOT EXISTS idx_lost_items_category_type ON lost_items(category, item_type);
CREATE INDEX IF NOT EXISTS idx_lost_items_reporter ON lost_items(reporter_id);

CREATE TABLE IF NOT EXISTS found_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    item_type TEXT NOT NULL,
    color TEXT,
    brand TEXT,
    found_location TEXT NOT NULL,
    found_datetime TEXT NOT NULL,
    date_to_claim TEXT,
    public_description TEXT,
    private_details TEXT,
    main_picture TEXT,
    additional_picture_1 TEXT,
    additional_picture_2 TEXT,
    additional_picture_3 TEXT,
    reporter_id INTEGER,
    claim_id INTEGER,
    processed_id TEXT,
    status TEXT NOT NULL DEFAULT 'found',
    created_at TEXT NOT NULL,
    FOREIGN KEY (reporter_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_found_items_status ON found_items(status);
CREATE INDEX IF NOT EXISTS idx_found_items_category_type ON found_items(category, item_type);
CREATE INDEX IF NOT EXISTS idx_found_items_reporter ON found_items(reporter_id);
CREATE INDEX IF NOT EXISTS idx_found_items_datetime ON found_items(found_datetime);

CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    found_item_id INTEGER,
    claimant_name TEXT NOT NULL,
    claimant_email TEXT NOT NULL,
    answers TEXT NOT NULL,
    verification_score INTEGER NOT NULL,
    decision TEXT NOT NULL DEFAULT 'pending',
    decision_reason TEXT,
    score_breakdown TEXT,
    pickup_datetime TEXT,
    pickup_location TEXT,
    handover_notes TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (found_item_id) REFERENCES found_items(id)
);

CREATE INDEX IF NOT EXISTS idx_claims_user ON claims(user_id);
CREATE INDEX IF NOT EXISTS idx_claims_item ON claims(found_item_id);
CREATE INDEX IF NOT EXISTS idx_claims_decision ON claims(decision);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    performed_by TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS token_blocklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jti TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
