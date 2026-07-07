-- ==========================================================
-- sms-forwarder
-- Application Database Schema
-- Version: 1.0
-- ==========================================================

-- ==========================================================
-- NOTE
-- Gammu manages the following tables:
--
--   inbox
--   outbox
--   outbox_multipart
--   sentitems
--   phones
--
-- Do NOT modify Gammu's schema.
-- This file only contains application-specific tables.
-- ==========================================================


-- ==========================================================
-- RETRY QUEUE
-- Stores messages that failed forwarding and require retry
-- ==========================================================

CREATE TABLE IF NOT EXISTS retry_queue (

    id SERIAL PRIMARY KEY,

    inbox_id INTEGER NOT NULL UNIQUE,

    retry_count INTEGER NOT NULL DEFAULT 0,

    status VARCHAR(20)
        NOT NULL
        DEFAULT 'PENDING'
        CHECK (
            status IN (
                'PENDING',
                'PROCESSING',
                'RETRY',
                'FAILED'
            )
        ),

    next_retry_time TIMESTAMP,

    last_error TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_retry_status
ON retry_queue(status);

CREATE INDEX IF NOT EXISTS idx_retry_next_time
ON retry_queue(next_retry_time);



-- ==========================================================
-- FORWARDED MESSAGES
-- Permanent archive of successfully forwarded SMS
-- ==========================================================

CREATE TABLE IF NOT EXISTS forwarded_messages (

    id SERIAL PRIMARY KEY,

    inbox_id INTEGER NOT NULL,

    sender VARCHAR(100) NOT NULL,

    message TEXT NOT NULL,

    received_at TIMESTAMP NOT NULL,

    forwarded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    http_status INTEGER,

    retry_count INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_forwarded_inbox
ON forwarded_messages(inbox_id);

CREATE INDEX IF NOT EXISTS idx_forwarded_sender
ON forwarded_messages(sender);

CREATE INDEX IF NOT EXISTS idx_forwarded_forwarded_at
ON forwarded_messages(forwarded_at);
