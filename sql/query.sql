CREATE SCHEMA IF NOT EXISTS url_shortener;

CREATE TABLE IF NOT EXISTS url_shortener.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS url_shortener.all_urls (
    id SERIAL PRIMARY KEY,
    original_url VARCHAR NOT NULL,
    slug_url VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    owner_id INTEGER REFERENCES url_shortener.users(id),
    CONSTRAINT idx_slug_url UNIQUE (slug_url)
);

CREATE TABLE IF NOT EXISTS url_shortener.url_tracking (
    id SERIAL PRIMARY KEY,
    url_id INTEGER REFERENCES url_shortener.all_urls(id),
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_slug_url ON url_shortener.all_urls (slug_url);