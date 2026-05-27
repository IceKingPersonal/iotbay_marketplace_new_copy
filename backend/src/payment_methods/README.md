# Feature 4 — Payment Methods

## Overview

This feature implements the Payment Methods module for the IoTBay system.
It allows users to:

- Add a payment method
- Edit a payment method
- Delete a payment method
- Search payment methods
- Validate input fields (card number, CVV, BSB, expiry date, etc.)

The backend is implemented using Flask and SQLite.

## Database Schema

Table: payment_methods

- id: INTEGER, primary key
- user_id: INTEGER, set to 1 for this assignment
- type: TEXT, Credit Card or Bank Account
- card_number: TEXT, 16-digit card number
- expiry_date: TEXT, MM/YY format
- cvv: TEXT, 3-digit CVV
- bsb: TEXT, 6-digit BSB
- account_number: TEXT, Bank account number

## API Endpoints

- GET /payment-methods
  - Returns all payment methods.
- POST /payment-methods/add
  - Adds a new payment method.
  - Form fields: type, card_number, expiry_date, cvv, bsb, account_number
- POST /payment-methods/edit/<id>
  - Updates an existing payment method.
- POST /payment-methods/delete/<id>
  - Deletes a payment method.

## How to Run

1. Navigate to the project folder:

cd iotbay

2. Run Flask:

python app.py

3. Open in browser:

http://127.0.0.1:5000/payment-methods