CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    result TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
