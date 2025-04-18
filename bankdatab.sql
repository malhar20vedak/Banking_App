CREATE DATABASE IF NOT EXISTS bank_nndb;
USE bank_nndb;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(10) NOT NULL CHECK (LENGTH(phone) = 10),
    dob DATE,
    address TEXT,
    uid VARCHAR(12) UNIQUE NOT NULL CHECK (LENGTH(uid) = 12),
    role ENUM('customer', 'teller', 'admin') DEFAULT 'customer'
);

-- Accounts Table
CREATE TABLE IF NOT EXISTS accounts (
    account_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED,
    balance DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id BIGINT UNSIGNED,
    type ENUM('Deposit', 'Withdraw', 'Transfer') NOT NULL,
    amount DECIMAL(10,2),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);
select * FROM users;
select * FROM transactions;
select * from accounts;
