-- Create reminders table
USE note_persistence;
GO;
CREATE TABLE
    reminders (
        id INTEGER NOT NULL,
        gmail VARCHAR(255) NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date TIMESTAMPTZ NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ,
        extensions JSONB, -- for future extensions
        PRIMARY KEY (gmail, id),
    );