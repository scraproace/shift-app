CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    goal_amount INTEGER NOT NULL DEFAULT 100000,
    is_valid BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    wage INTEGER NOT NULL,
    has_night_wage BOOLEAN NOT NULL,
    closing_day INTEGER NOT NULL,
    pay_day INTEGER NOT NULL,
    is_valid BOOLEAN NOT NULL DEFAULT true,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE shifts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    place_id INTEGER NOT NULL,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    break_time INTERVAL NOT NULL,
    is_valid BOOLEAN NOT NULL DEFAULT true,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (place_id) REFERENCES places (id)
);
