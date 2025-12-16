CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
);

CREATE TABLE chat_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_role TEXT,
    session_title TEXT NOT NULL,
    temp REAL NOT NULL CHECK (temp >= 0 AND temp <= 2),
    session_created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    message_role TEXT NOT NULL CHECK (message_role IN ('user', 'assistant', 'system')),
    message_content TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id),
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE INDEX idx_messages_user_session_id ON messages (user_id, session_id, message_id);
CREATE INDEX idx_chat_sessions_user_created ON chat_sessions (user_id, session_created_at DESC);