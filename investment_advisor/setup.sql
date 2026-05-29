DROP DATABASE IF EXISTS investment_advisor;
CREATE DATABASE investment_advisor;
USE investment_advisor;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    age INT NOT NULL,
    income DECIMAL(15,2) NOT NULL,
    savings DECIMAL(15,2) NOT NULL,
    debts DECIMAL(15,2) NOT NULL,
    goals VARCHAR(255) NOT NULL,
    investment_horizon INT NOT NULL,
    risk_tolerance VARCHAR(50) NOT NULL,
    monthly_expenses DECIMAL(15,2) NOT NULL,
    dependents INT DEFAULT 0,
    employment_status VARCHAR(50) DEFAULT 'employed',
    existing_investments VARCHAR(255) DEFAULT 'none',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    profile_id INT NOT NULL,
    stocks_pct DECIMAL(5,2) DEFAULT 0,
    bonds_pct DECIMAL(5,2) DEFAULT 0,
    mutual_funds_pct DECIMAL(5,2) DEFAULT 0,
    gold_pct DECIMAL(5,2) DEFAULT 0,
    real_estate_pct DECIMAL(5,2) DEFAULT 0,
    cash_pct DECIMAL(5,2) DEFAULT 0,
    risk_label VARCHAR(50) NOT NULL,
    certainty_factor DECIMAL(5,4) NOT NULL,
    risk_score INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);

CREATE TABLE rule_trace (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recommendation_id INT NOT NULL,
    rule_id VARCHAR(50) NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    condition_matched TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    certainty_factor DECIMAL(5,4) NOT NULL,
    priority INT NOT NULL,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recommendation_id) REFERENCES recommendations(id) ON DELETE CASCADE
);

CREATE TABLE scenarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scenario_name VARCHAR(255) NOT NULL,
    profile_snapshot JSON NOT NULL,
    recommendation_snapshot JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

select*from users;
select*from user_profiles;
select*from rule_trace;
select*from recommendations;
select*from scenarios;
