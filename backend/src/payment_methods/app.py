from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------------------
# Database helper
# ---------------------------
def get_db_connection():
    conn = sqlite3.connect('database/iotbay.db')
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------
# Validation functions
# ---------------------------
def validate_payment_method(data):
    errors = []

    if data["type"] == "Credit Card":
        if not re.fullmatch(r"\d{16}", data["card_number"]):
            errors.append("Card number must be 16 digits.")
        if not re.fullmatch(r"\d{3}", data["cvv"]):
            errors.append("CVV must be 3 digits.")
        if not re.fullmatch(r"\d{2}/\d{2}", data["expiry_date"]):
            errors.append("Expiry date must be in MM/YY format.")

    if data["type"] == "Bank Account":
        if not re.fullmatch(r"\d{6}", data["bsb"]):
            errors.append("BSB must be 6 digits.")
        if not re.fullmatch(r"\d+", data["account_number"]):
            errors.append("Account number must be digits only.")

    return errors


# ---------------------------
# READ
# ---------------------------
@app.route('/payment-methods')
def payment_methods():
    search = request.args.get("search", "")

    conn = get_db_connection()
    if search:
        rows = conn.execute(
            "SELECT * FROM payment_methods WHERE type LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM payment_methods").fetchall()

    conn.close()
    return render_template("payment_methods.html", methods=rows, search=search)


# ---------------------------
# CREATE
# ---------------------------
@app.route('/payment-methods/add', methods=['GET', 'POST'])
def add_payment_method():
    if request.method == 'POST':
        data = {
            "user_id": 1,
            "type": request.form['type'],
            "card_number": request.form.get('card_number', ''),
            "expiry_date": request.form.get('expiry_date', ''),
            "cvv": request.form.get('cvv', ''),
            "bsb": request.form.get('bsb', ''),
            "account_number": request.form.get('account_number', '')
        }

        errors = validate_payment_method(data)
        if errors:
            for e in errors:
                flash(e)
            return redirect(url_for('add_payment_method'))

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO payment_methods (user_id, type, card_number, expiry_date, cvv, bsb, account_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data["user_id"], data["type"], data["card_number"], data["expiry_date"],
              data["cvv"], data["bsb"], data["account_number"]))
        conn.commit()
        conn.close()

        flash("Payment method added successfully!")
        return redirect(url_for('payment_methods'))

    return render_template("add_payment_method.html")


# ---------------------------
# UPDATE
# ---------------------------
@app.route('/payment-methods/edit/<int:id>', methods=['GET', 'POST'])
def edit_payment_method(id):
    conn = get_db_connection()
    method = conn.execute("SELECT * FROM payment_methods WHERE id = ?", (id,)).fetchone()

    if not method:
        flash("Payment method not found.")
        return redirect(url_for('payment_methods'))

    if request.method == 'POST':
        data = {
            "type": request.form['type'],
            "card_number": request.form.get('card_number', ''),
            "expiry_date": request.form.get('expiry_date', ''),
            "cvv": request.form.get('cvv', ''),
            "bsb": request.form.get('bsb', ''),
            "account_number": request.form.get('account_number', '')
        }

        errors = validate_payment_method(data)
        if errors:
            for e in errors:
                flash(e)
            return redirect(url_for('edit_payment_method', id=id))

        conn.execute("""
            UPDATE payment_methods
            SET type=?, card_number=?, expiry_date=?, cvv=?, bsb=?, account_number=?
            WHERE id=?
        """, (data["type"], data["card_number"], data["expiry_date"], data["cvv"],
              data["bsb"], data["account_number"], id))
        conn.commit()
        conn.close()

        flash("Payment method updated successfully!")
        return redirect(url_for('payment_methods'))

    conn.close()
    return render_template("edit_payment_method.html", method=method)


# ---------------------------
# DELETE
# ---------------------------
@app.route('/payment-methods/delete/<int:id>', methods=['POST'])
def delete_payment_method(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM payment_methods WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Payment method deleted successfully!")
    return redirect(url_for('payment_methods'))


# ---------------------------
# Home page
# ---------------------------
@app.route('/')
def home():
    return "Flask is running!"


if __name__ == '__main__':
    app.run(debug=True)
