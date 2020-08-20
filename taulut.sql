CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    topic TEXT,
    description TEXT,
    hashtags TEXT,
    created_at TIMESTAMP
);

CREATE TABLE frontside (
    id SERIAL PRIMARY KEY,
    deck_id INTEGER REFERENCES decks,
    word TEXT
);

CREATE TABLE backside (
    id SERIAL PRIMARY KEY,
    frontside_id INTEGER REFERENCES frontside,
    answer TEXT
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(14) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INTEGER REFERENCES users, 
    deck_id INTEGER REFERENCES decks,
    sent_at TIMESTAMP
);

