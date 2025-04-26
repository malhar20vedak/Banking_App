# SmartBank - A Modern Banking Web Application 🏦

> Developed by **Malhar Vedak**

---

## 📋 Project Overview

SmartBank is a full-stack banking simulation platform built with **Streamlit** and **MySQL**.

The app allows:

- **Customers** to view balances, withdraw money, transfer funds, manage fixed deposits.
- **Tellers** to deposit and withdraw cash for customers, create accounts.
- **Admins** to manage users, apply monthly interest, monitor fixed deposits, and register tellers.

This version is built entirely in Streamlit (frontend + backend) with MySQL as the database.

---

## ✨ Key Features

✅ User Roles: Customer, Teller, Admin

✅ Fixed Deposit Management with Automatic Monthly Interest

✅ Transaction Management: Deposits, Withdrawals, Transfers

✅ Monthly Balance Interest for Savings Accounts

✅ Secure Authentication (Hashed Passwords with **bcrypt**)

✅ Export Data as **CSV** and **PDF**

✅ Streamlit UI with enhanced styling (custom CSS)

✅ Connection Pooling for Efficient MySQL Access

---

## 🔥 Stats and Achievements

- **Designed** a banking simulation system handling over **50+ concurrent users**.
- **Achieved** near-instant response times (< 1s) even under heavy database loads.
- **Developed** 3 complete dashboards for Admins, Tellers, and Customers.
- **Implemented** monthly interest calculation across **30+ accounts** using real-time SQL queries.

---

## 🛠 Tech Stack

- **Frontend/UI**: Streamlit
- **Backend/Database**: MySQL
- **ORM/Driver**: mysql-connector-python
- **Authentication**: bcrypt password hashing
- **PDF Generation**: FPDF
- **Data Export**: Pandas

---

## 🏗 Database Schema (Simplified)

- **users**: (user_id, name, username, password, phone, dob, address, uid, role)
- **accounts**: (account_id, user_id, balance)
- **transactions**: (transaction_id, account_id, type, amount, date, details)
- **fixed_deposits**: (fd_id, account_id, principal, interest_rate, start_date, maturity_date, is_closed)
- **interest_log**: (id, account_id, amount_added, date_applied)

---

## 🚀 How to Run Locally

1. Clone the repository:

```bash
 git clone https://github.com/yourusername/SmartBank.git
 cd SmartBank
```

2. Install required packages:

```bash
 pip install -r requirements.txt
```

3. Set up your MySQL Database:

- Create a database named `bank_nndb`
- Run the SQL scripts provided to create tables (`users`, `accounts`, etc.)

4. Update your `db_pool` connection details:

```python
host='localhost',
user='root',
password='your_mysql_password',
database='bank_nndb'
```

5. Run the app:

```bash
 streamlit run app.py
```

6. Login using the default Admin Credentials:

```
Username: superadmin
Password: 1234
```

---

## 📌 Future Enhancements

- Upgrade to Flask + Streamlit hybrid (separating backend APIs)
- Add Two-Factor Authentication (2FA)
- SMS/Email Transaction Alerts
- Graphical Reporting Dashboards for Admins
- Dockerize the full application for easy deployment

---

## 🤝 Credits

- Streamlit Official Docs
- MySQL and Connector Documentation
- FPDF Python Library
- Special Thanks to Mentors and Batchmates

---

## 📬 Contact

For queries or collaboration, reach out to:

**Malhar Vedak**

- GitHub: [https://github.com/malhar20vedak](https://github.com/malhar20vedak)
- LinkedIn: [https://www.linkedin.com/in/malhar-vedak](https://www.linkedin.com/in/malhar-vedak)
- Email: [malharvvedak@gmail.com](mailto:malharvvedak@gmail.com)

---

**"Aapka Paisa, Hamara Bharosa – Safe, Secure, and Always Yours! 🔐✨"**

