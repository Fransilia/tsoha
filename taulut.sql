CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(14) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    topic TEXT,
    description TEXT,
    user_id INTEGER REFERENCES users,
    created_at TIMESTAMP
);

CREATE TABLE frontside (
    id SERIAL PRIMARY KEY,
    deck_id INTEGER REFERENCES decks,
    word TEXT,
    answer TEXT
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INTEGER REFERENCES users, 
    deck_id INTEGER REFERENCES decks,
    sent_at TIMESTAMP
);

CREATE TABLE hard (
    PRIMARY KEY (user_id, frontside_id),
    user_id INTEGER REFERENCES users,
    frontside_id INTEGER REFERENCES frontside 
);

