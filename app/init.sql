CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    subject TEXT,
    sender TEXT,
    date TEXT,
    body TEXT
);
