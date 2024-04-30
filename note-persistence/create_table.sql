CREATE TABLE
    reminders (
        id INTEGER NOT NULL,
        chat_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ,
        extensions JSONB, -- for future extensions
        PRIMARY KEY (chat_id, id)
    );


CREATE TABLE
    reminder_delivery (
        id INTEGER NOT NULL,
        chat_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date TIMESTAMPTZ NOT NULL,
        n_retries INTEGER DEFAULT 0,
        last_retry TIMESTAMPTZ,
        PRIMARY KEY (chat_id, id)
    );

