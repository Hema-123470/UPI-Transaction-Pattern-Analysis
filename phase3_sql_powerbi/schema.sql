-- =============================================================
-- schema.sql
-- UPI Transaction Pattern Analysis – MySQL Database Schema
-- =============================================================
-- Database  : upi_transaction_analysis
-- Tables    : transactions (main fact table)
--             dim_category, dim_bank, dim_state, dim_upi_app
-- =============================================================

-- Create and select database
CREATE DATABASE IF NOT EXISTS upi_transaction_analysis
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE upi_transaction_analysis;

-- ── Dimension: Category ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_category (
    category_id   INT           NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(50)   NOT NULL,
    PRIMARY KEY (category_id),
    UNIQUE KEY uq_category (category_name)
);

-- ── Dimension: Bank ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_bank (
    bank_id   INT         NOT NULL AUTO_INCREMENT,
    bank_name VARCHAR(60) NOT NULL,
    PRIMARY KEY (bank_id),
    UNIQUE KEY uq_bank (bank_name)
);

-- ── Dimension: State ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_state (
    state_id   INT         NOT NULL AUTO_INCREMENT,
    state_name VARCHAR(60) NOT NULL,
    PRIMARY KEY (state_id),
    UNIQUE KEY uq_state (state_name)
);

-- ── Dimension: UPI App ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_upi_app (
    app_id   INT         NOT NULL AUTO_INCREMENT,
    app_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (app_id),
    UNIQUE KEY uq_app (app_name)
);

-- ── Fact: Transactions ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id                 INT           NOT NULL AUTO_INCREMENT,
    transaction_id     VARCHAR(40)   NOT NULL,
    transaction_date   DATE          NOT NULL,
    transaction_time   TIME          NOT NULL,
    day_of_week        VARCHAR(12)   NOT NULL,
    month_name         VARCHAR(12)   NOT NULL,
    month_num          TINYINT       NOT NULL,
    week_of_year       TINYINT       NOT NULL,
    hour               TINYINT       NOT NULL,
    time_of_day        VARCHAR(12)   NOT NULL,
    is_weekend         TINYINT(1)    NOT NULL DEFAULT 0,
    sender_upi         VARCHAR(60)   NOT NULL,
    receiver_upi       VARCHAR(60)   NOT NULL,
    sender_bank        VARCHAR(60)   NOT NULL,
    receiver_bank      VARCHAR(60)   NOT NULL,
    upi_app            VARCHAR(50)   NOT NULL,
    amount             DECIMAL(12,2) NOT NULL,
    payment_type       VARCHAR(5)    NOT NULL,
    category           VARCHAR(50)   NOT NULL,
    state              VARCHAR(60)   NOT NULL,
    city               VARCHAR(60)   NOT NULL,
    device             VARCHAR(30)   NOT NULL,
    status             VARCHAR(10)   NOT NULL,
    reference_no       VARCHAR(15)   NOT NULL,
    remarks            VARCHAR(120)  NOT NULL,
    amount_bucket      VARCHAR(25)   NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_txn (transaction_id),
    KEY idx_date      (transaction_date),
    KEY idx_status    (status),
    KEY idx_category  (category),
    KEY idx_bank      (sender_bank),
    KEY idx_state     (state),
    KEY idx_app       (upi_app),
    KEY idx_ptype     (payment_type),
    KEY idx_hour      (hour),
    KEY idx_month     (month_num)
);
