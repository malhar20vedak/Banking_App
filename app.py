import streamlit as st
import bcrypt
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from fpdf import FPDF
from mysql.connector import Error, IntegrityError, pooling
import mysql.connector
from decimal import Decimal

# Must be the first Streamlit command
st.set_page_config(page_title="SmartBank", page_icon="🏦", layout="wide")


# def get_db_connection():
#     return mysql.connector.connect(
#         host='localhost',
#         user='root',            # Change this
#         password='Aman@6006',  # Change this
#         database='bank_ndb',
#         autocommit=True
#     )

db_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host="localhost",
    user="root",
    password="Aman@6006",
    database="bank_nndb"
)

def get_db_connection():
    return db_pool.get_connection()

# Apply light theme styling
st.markdown("""
    <style>
        body {
            background-color: #f8f9fa; /* Light Background */
            font-family: 'Arial', sans-serif;
        }
        .title-text {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: #1E3A8A; /* Dark Blue */
        }
        .subtitle-text {
            text-align: center;
            font-size: 24px;
            color: #2563EB; /* Lighter Blue */
        }
        .form-title {
            font-size: 22px;
            font-weight: bold;
            color: #333;
            text-align: left;
        }
        .stButton > button {
            background-color: #2563EB !important; 
            color: white !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            padding: 10px !important;
        }
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 1px solid #ddd !important;
            padding: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)

def export_to_csv(data, filename="data.csv"):
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📄 Download as CSV", csv, file_name=filename, mime='text/csv')

def ensure_interest_log_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interest_log (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            account_id INTEGER,
            amount_added REAL,
            date_applied TEXT
        )
    """)
    conn.commit()
    conn.close()

def validate_account(cursor, acc_id):
    cursor.execute("SELECT 1 FROM accounts WHERE account_id = %s", (acc_id,))
    return cursor.fetchone() is not None

def get_account_holder_name(cursor, acc_id):
    cursor.execute("""
        SELECT u.name FROM users u
        JOIN accounts a ON u.user_id = a.user_id
        WHERE a.account_id = %s
    """, (acc_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def confirm_and_execute_transaction(label, action_fn):
    if st.button(label, use_container_width=True):
        if st.checkbox("✅ Confirm transaction before proceeding"):
            action_fn()
        else:
            st.warning("⚠️ Please confirm the transaction checkbox before proceeding.")

def reset_password():
    st.subheader("🔐 Reset Password")
    username = st.text_input("Enter your username")
    dob = st.date_input("Confirm your Date of Birth")
    new_pwd = st.text_input("New 4-digit Password", type="password")
    confirm_pwd = st.text_input("Confirm New Password", type="password")

    if st.button("Reset Password", use_container_width=True):
        if new_pwd != confirm_pwd:
            st.error("❌ Passwords do not match.")
            return
        if not re.fullmatch(r"\d{4}", new_pwd):
            st.error("❌ Password must be exactly 4 digits.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = %s AND dob = %s", (username, dob))
        user = cursor.fetchone()

        if user:
            hashed = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (hashed, user[0]))
            conn.commit()
            st.success("✅ Password has been reset successfully.")
        else:
            st.error("❌ User not found or DOB incorrect.")
        conn.close()


def create_admin_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    username = "superadmin"
    password = "1234"
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("""
            INSERT INTO users (name, username, password, phone, dob, address, uid, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'admin')
        """, (
            "Admin User",
            username,
            hashed_password,
            "9999999999",
            "1970-01-01",
            "Admin Address",
            "000000000000"
        ))
        conn.commit()
        st.success("✅ Admin account created: superadmin / 1234")
    except mysql.connector.errors.IntegrityError:
        st.warning("⚠️ Admin account already exists.")
    finally:
        conn.close()



# Function to handle registration
def register_user():
    st.markdown("<h3 class='form-title'>📝 Register a New Account</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="Enter your full name")
        username = st.text_input("Choose a Username", placeholder="Pick a unique username")
        password = st.text_input("4-digit Password", type='password', placeholder="****")
        phone = st.text_input("Phone Number (10 digits)", placeholder="1234567890")
        dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())

    with col2:
        uid = st.text_input("UID (12-digit Aadhaar)", placeholder="123412341234")
        address = st.text_area("Address", placeholder="Enter your complete address")
        role = st.selectbox("Role", ["customer", "teller"])

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Login"):
            st.session_state['show_register'] = False
            st.rerun()
    with col2:
        if st.button("✅ Register"):
            if not re.fullmatch(r"\d{4}", password) or len(phone) != 10 or len(uid) != 12:
                st.error("❌ Please correct errors before submitting.")
            else:
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                conn = get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO users (name, username, password, phone, dob, address, uid, role)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (name, username, hashed_password, phone, dob, address, uid, role))
                    conn.commit()
                    st.success("✅ Registration successful! You can now log in.")
                except mysql.connector.errors.IntegrityError:
                    st.error("❌ Username already exists. Choose a different one.")
                conn.close()

# # Function to handle login
# def login():
#     st.markdown("<h3 class='form-title'>🔑 Login to Your Account</h3>", unsafe_allow_html=True)
    
#     username = st.text_input("Username", placeholder="Enter your username")
#     password = st.text_input("Password", type='password', placeholder="Enter your password")
    
#     if st.button("Login"):
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT user_id, password, role FROM users WHERE username = %s", (username,))
#         user = cursor.fetchone()
#         conn.close()
#         if user and bcrypt.checkpw(password.encode(), user[1]):
#             st.session_state['user_id'] = user[0]
#             st.session_state['role'] = user[2]
#             st.success(f"✅ Welcome, {username}")
#             st.rerun()
#         else:
#             st.error("❌ Invalid username or password")
    
#     if st.button("Don't have an account? Register here"):
#         st.session_state['show_register'] = True
#         st.rerun()

# import bcrypt
# import streamlit as st

def login():
    st.markdown("<h3 class='form-title'>🔑 Login to Your Account</h3>", unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type='password', placeholder="Enter your password")
    
    if st.button("Login"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            stored_password = user[1]  # Password from DB

            # ✅ Ensure stored password is in bytes before comparing
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                st.session_state['user_id'] = user[0]
                st.session_state['role'] = user[2]
                st.success(f"✅ Welcome, {username}")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        else:
            st.error("❌ Invalid username or password")
    
    if st.button("Don't have an account? Register here"):
        st.session_state['show_register'] = True
        st.rerun()


def admin_dashboard():
    st.subheader("🛡️ Admin Dashboard")
    search = st.text_input("Search by Name or Username")

    conn = get_db_connection()
    cursor = conn.cursor()
    if search:
        cursor.execute("""
            SELECT user_id, name, username, phone, uid, role 
            FROM users 
            WHERE name LIKE %s OR username LIKE %s
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT user_id, name, username, phone, uid, role FROM users")
    users = cursor.fetchall()

    df = pd.DataFrame(users, columns=["User ID", "Name", "Username", "Phone", "UID", "Role"])
    st.dataframe(df, use_container_width=True)
    export_to_csv(df, filename="user_data.csv")

    user_ids = [str(row[0]) for row in users if row[5] != 'admin']
    selected_id = st.selectbox("Select User ID to Delete (non-admin only)", user_ids)
    if st.button("Delete Selected User", use_container_width=True):
        cursor.execute("DELETE FROM users WHERE user_id = %s", (selected_id,))
        cursor.execute("DELETE FROM accounts WHERE user_id = %s", (selected_id,))
        conn.commit()
        st.success("✅ User and associated accounts deleted.")

    if st.button("Apply Monthly Interest to All Accounts", use_container_width=True):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Fetch all accounts
            cursor.execute("SELECT account_id, balance FROM accounts")
            accounts = cursor.fetchall()  # Ensure results are fetched completely

            if not accounts:
                st.warning("⚠️ No accounts found.")
            else:
                for acc_id, balance in accounts:
                    interest = round(float(balance) * 0.005, 2)  # Convert Decimal to float
                    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (interest, acc_id))
                    cursor.execute("INSERT INTO interest_log (account_id, amount_added, date_applied) VALUES (%s, %s, CURDATE())", (acc_id, interest))

                conn.commit()
                st.success("✅ Monthly interest applied and recorded for all accounts.")

        except mysql.connector.Error as e:
            st.error(f"❌ Database Error: {e}")
        
        except Exception as e:
            st.error(f"❌ Unexpected Error: {e}")

        finally:
            cursor.close()
            conn.close()
        st.markdown("### 📊 Interest Calculation History")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interest_log ORDER BY date_applied DESC")
    interest_data = cursor.fetchall()
    conn.close()

    if interest_data:
        df = pd.DataFrame(interest_data, columns=["Log ID", "Account ID", "Amount Added", "Date Applied"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No interest records found.")

    st.markdown("---")
    st.subheader("🔑 Change Admin Password")
    current_pwd = st.text_input("Current Password", type="password")
    new_pwd = st.text_input("New 4-digit Password", type="password")
    confirm_pwd = st.text_input("Confirm New Password", type="password")

    if st.button("Change Password", use_container_width=True):
        if not re.fullmatch(r"\d{4}", new_pwd):
            st.error("❌ New password must be exactly 4 digits.")
        elif new_pwd != confirm_pwd:
            st.error("❌ Passwords do not match.")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE user_id = %s", (st.session_state['user_id'],))
            stored_hash = cursor.fetchone()
            if stored_hash and bcrypt.checkpw(current_pwd.encode(), stored_hash[0]):
                new_hashed = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt())
                cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_hashed, st.session_state['user_id']))
                conn.commit()
                st.success("✅ Password updated successfully.")
            else:
                st.error("❌ Current password is incorrect.")
            conn.close()

    if st.button("Logout", use_container_width=True):
        del st.session_state['user_id']
        del st.session_state['role']
        st.rerun()

def teller_dashboard():
    st.subheader("🏦 Teller Dashboard")

    # ✅ Display post-transaction message if available
    if 'message' in st.session_state:
        st.success(st.session_state['message'])
        del st.session_state['message']

    # ✅ Initialize session state keys
    # for key in ['deposit_acc_input', 'deposit_amt_input', 'withdraw_acc_input', 'withdraw_amt_input']:
    #     if key not in st.session_state:
    #         st.session_state[key] = "" if 'acc' in key else 0.0

    option = st.radio("Choose an operation", ["Deposit", "Withdraw", "Create Account", "Export Transactions"], horizontal=True)

    # if option == "Deposit":
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         acc_id = st.text_input("💳 Enter Customer Account ID", key='deposit_acc_input')
    #     with col2:
    #         # Ensure session state has a valid amount
    #         if "deposit_amt_input" not in st.session_state or st.session_state["deposit_amt_input"] < 0.01:
    #             st.session_state["deposit_amt_input"] = 0.01  # Set valid initial value

    #         # Number input field
    #         amount = st.number_input(
    #             "💰 Enter Amount",
    #             min_value=0.01,
    #             step=0.01,
    #             key="deposit_amt_input"
    #         )




    #     if acc_id:
    #         try:
    #             acc_id_int = int(acc_id)
    #             conn = get_db_connection()
    #             cursor = conn.cursor()
    #             name = get_account_holder_name(cursor, acc_id_int)
    #             if name:
    #                 cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (acc_id_int,))
    #                 balance_row = cursor.fetchone()
    #                 balance_before = balance_row[0] if balance_row else 0
    #                 st.info(f"👤 Account Holder: {name}")
    #                 st.metric("Current Balance", f"₹{balance_before}")
    #                 st.metric("New Balance (After Deposit)", f"₹{balance_before + amount}")

    #                 st.markdown(f"""
    #                     ### ✅ Confirm Transaction
    #                     - Account Holder: {name}
    #                     - Amount: ₹{amount}
    #                     - Type: Deposit
    #                 """)
    #                 confirm = st.checkbox("I confirm the above details are correct.")

    #                 if st.button("✅ Deposit Now", use_container_width=True):
    #                     if confirm:
    #                         cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, acc_id_int))
    #                         cursor.execute("INSERT INTO transactions (account_id, type, amount, date, details) VALUES (%s, 'Deposit', %s, CURDATE(), %s)", (acc_id_int, amount, 'Deposited by teller'))
    #                         conn.commit()
    #                         conn.close()
    #                         st.session_state['message'] = f"✅ Deposited ₹{amount} into account {acc_id_int}"
    #                         st.rerun()
    #                     else:
    #                         st.warning("⚠️ Please confirm the transaction checkbox before proceeding.")
    #                         conn.close()
    #             else:
    #                 st.warning("⚠️ No such account found.")
    #                 conn.close()
    #         except ValueError:
    #             st.error("❌ Account ID must be a number.")
    from decimal import Decimal

    if option == "Deposit":
        col1, col2 = st.columns(2)
        with col1:
            acc_id = st.text_input("💳 Enter Customer Account ID", key='deposit_acc_input')
        with col2:
            # Ensure session state has a valid amount
            if "deposit_amt_input" not in st.session_state or st.session_state["deposit_amt_input"] < 0.01:
                st.session_state["deposit_amt_input"] = 0.01  # Set valid initial value

            # Number input field
            amount = st.number_input(
                "💰 Enter Amount",
                min_value=0.01,
                step=0.01,
                key="deposit_amt_input"
            )

        if acc_id:
            try:
                acc_id_int = int(acc_id)
                conn = get_db_connection()
                cursor = conn.cursor()
                name = get_account_holder_name(cursor, acc_id_int)
                if name:
                    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (acc_id_int,))
                    balance_row = cursor.fetchone()
                    balance_before = balance_row[0] if balance_row else 0

                    # Convert balance_before and amount to decimal.Decimal
                    balance_before = Decimal(str(balance_before))  # Convert to Decimal
                    amount = Decimal(str(amount))  # Convert to Decimal

                    st.info(f"👤 Account Holder: {name}")
                    st.metric("Current Balance", f"₹{balance_before}")
                    st.metric("New Balance (After Deposit)", f"₹{balance_before + amount}")

                    st.markdown(f"""
                        ### ✅ Confirm Transaction
                        - Account Holder: {name}
                        - Amount: ₹{amount}
                        - Type: Deposit
                    """)
                    confirm = st.checkbox("I confirm the above details are correct.")

                    if st.button("✅ Deposit Now", use_container_width=True):
                        if confirm:
                            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, acc_id_int))
                            cursor.execute("INSERT INTO transactions (account_id, type, amount, date, details) VALUES (%s, 'Deposit', %s, CURDATE(), %s)", (acc_id_int, amount, 'Deposited by teller'))
                            conn.commit()
                            conn.close()
                            st.session_state['message'] = f"✅ Deposited ₹{amount} into account {acc_id_int}"
                            st.rerun()
                        else:
                            st.warning("⚠️ Please confirm the transaction checkbox before proceeding.")
                            conn.close()
                else:
                    st.warning("⚠️ No such account found.")
                    conn.close()
            except ValueError:
                st.error("❌ Account ID must be a number.")

    # elif option == "Withdraw":
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         acc_id = st.text_input("💳 Enter Customer Account ID", key='withdraw_acc_input')
    #     with col2:
    #         amount = st.number_input("💸 Enter Amount", min_value=0.01, key='withdraw_amt_input')

    #     if acc_id:
    #         try:
    #             acc_id_int = int(acc_id)
    #             conn = get_db_connection()
    #             cursor = conn.cursor()
    #             name = get_account_holder_name(cursor, acc_id_int)
    #             if name:
    #                 cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (acc_id_int,))
    #                 balance = cursor.fetchone()
    #                 st.info(f"👤 Account Holder: {name}")
    #                 st.metric("Current Balance", f"₹{balance[0]}")
    #                 st.metric("New Balance (After Withdrawal)", f"₹{balance[0] - amount}")

    #                 st.markdown(f"""
    #                     ### ✅ Confirm Transaction
    #                     - Account Holder: {name}
    #                     - Amount: ₹{amount}
    #                     - Type: Withdraw
    #                 """)
    #                 confirm = st.checkbox("I confirm the above details are correct.")

    #                 if st.button("✅ Withdraw Now", use_container_width=True):
    #                     if confirm:
    #                         if balance and balance[0] >= amount:
    #                             cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, acc_id_int))
    #                             cursor.execute("INSERT INTO transactions (account_id, type, amount, date, details) VALUES (%s, 'Withdraw', %s, CURDATE(), %s)", (acc_id_int, -amount, 'Withdrawn by teller'))
    #                             conn.commit()
    #                             conn.close()
    #                             # for key in ['withdraw_acc_input', 'withdraw_amt_input']:
    #                             #     if key in st.session_state:
    #                             #         st.session_state[key] = "" if 'acc' in key else 0.0
    #                             st.session_state['message'] = f"✅ Withdrawn ₹{amount} from account {acc_id_int}"
    #                             st.rerun()
    #                         else:
    #                             st.error("❌ Insufficient balance.")
    #                             conn.close()
    #                     else:
    #                         st.warning("⚠️ Please confirm the transaction checkbox before proceeding.")
    #                         conn.close()
    #             else:
    #                 st.warning("⚠️ No such account found.")
    #                 conn.close()
    #         except ValueError:
    #             st.error("❌ Account ID must be a number.")

    elif option == "Withdraw":
        col1, col2 = st.columns(2)
        with col1:
            acc_id = st.text_input("💳 Enter Customer Account ID", key='withdraw_acc_input')
        with col2:
            amount = st.number_input("💸 Enter Amount", min_value=0.01, key='withdraw_amt_input')

        if acc_id:
            try:
                acc_id_int = int(acc_id)
                conn = get_db_connection()
                cursor = conn.cursor()
                name = get_account_holder_name(cursor, acc_id_int)
                if name:
                    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (acc_id_int,))
                    balance = cursor.fetchone()

                    # Convert balance and amount to Decimal for precise arithmetic
                    balance_decimal = Decimal(str(balance[0]))  # Convert balance to Decimal
                    amount_decimal = Decimal(str(amount))  # Convert amount to Decimal

                    st.info(f"👤 Account Holder: {name}")
                    st.metric("Current Balance", f"₹{balance_decimal}")
                    st.metric("New Balance (After Withdrawal)", f"₹{balance_decimal - amount_decimal}")

                    st.markdown(f"""
                        ### ✅ Confirm Transaction
                        - Account Holder: {name}
                        - Amount: ₹{amount}
                        - Type: Withdraw
                    """)
                    confirm = st.checkbox("I confirm the above details are correct.")

                    if st.button("✅ Withdraw Now", use_container_width=True):
                        if confirm:
                            if balance_decimal >= amount_decimal:
                                # Proceed with the withdrawal
                                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount_decimal, acc_id_int))
                                cursor.execute("INSERT INTO transactions (account_id, type, amount, date, details) VALUES (%s, 'Withdraw', %s, CURDATE(), %s)", (acc_id_int, -amount_decimal, 'Withdrawn by teller'))
                                conn.commit()
                                st.session_state['message'] = f"✅ Withdrawn ₹{amount} from account {acc_id_int}"
                                st.rerun()
                            else:
                                st.error("❌ Insufficient balance.")
                        else:
                            st.warning("⚠️ Please confirm the transaction checkbox before proceeding.")
                    conn.close()
                else:
                    st.warning("⚠️ No such account found.")
                    conn.close()
            except ValueError:
                st.error("❌ Account ID must be a number.")





    # elif option == "Create Account":
    #     username = st.text_input("Enter Username to Create Account")
    #     if st.button("Create Account", use_container_width=True):
    #         conn = get_db_connection()
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    #         user = cursor.fetchone()
    #         if user:
    #             cursor.execute("INSERT INTO accounts (user_id, balance) VALUES (%s, %s)", (user[0], 0))
    #             conn.commit()
    #             st.success(f"✅ Account created successfully for {username}")
    #         else:
    #             st.error("❌ No such username found.")
    #         conn.close()
    elif option == "Create Account":
        username = st.text_input("Enter Username to Create Account")
        
        if st.button("Create Account", use_container_width=True):
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if the user exists
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user:
                user_id = user[0]

                # Ensure any previous results are fully consumed before running the next query
                cursor.fetchall()  # This prevents the "Unread result found" error
                
                try:
                    # Insert a new account for the user
                    cursor.execute("INSERT INTO accounts (user_id, balance) VALUES (%s, %s)", (user_id, 0))
                    conn.commit()

                    # Fetch the newly created account ID
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    account_id = cursor.fetchone()[0]  # Get the last inserted account ID
                    
                    st.success(f"✅ Account created successfully for {username}")
                    st.info(f"🆔 New Account ID: {account_id}")

                except Exception as e:
                    st.error(f"❌ Error creating account: {e}")
            
            else:
                st.error("❌ No such username found.")

            cursor.close()
            conn.close()


    elif option == "Export Transactions":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        conn.close()

        if transactions:
            st.dataframe(transactions, use_container_width=True)
            export_to_csv(transactions, filename="transactions.csv")
            export_to_pdf(transactions, filename="transaction_history.pdf")
            
        else:
            st.write("No transactions found.")

    if st.button("Logout", use_container_width=True):
        del st.session_state['user_id']
        del st.session_state['role']
        st.rerun()


def export_to_pdf(data, filename="transactions.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Transaction History", ln=True, align='C')

    col_width = pdf.w / 6
    row_height = 8
    headers = ["Txn ID", "Account ID", "Type", "Amount", "Date", "Details"]
    for header in headers:
        pdf.cell(col_width, row_height, txt=header, border=1)
    pdf.ln(row_height)

    for row in data:
        for item in row:
            pdf.cell(col_width, row_height, txt=str(item), border=1)
        pdf.ln(row_height)

    pdf.output(filename)
    with open(filename, "rb") as f:
        st.download_button("🧾 Download as PDF", f.read(), file_name=filename, mime='application/pdf')


def show_notifications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, amount, date, details FROM transactions 
        WHERE account_id IN (SELECT account_id FROM accounts WHERE user_id = %s)
        ORDER BY date DESC LIMIT 5
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    st.markdown("### 🔔 Recent Notifications")
    if rows:
        for txn in rows:
            st.info(f"{txn[2]} • {txn[0]} • ₹{txn[1]} • {txn[3]}")
    else:
        st.info("No recent transactions found.")


def customer_dashboard():
    st.subheader("👤 Customer Dashboard")
    show_notifications(st.session_state['user_id'])
    option = st.radio("Choose an operation", ["View Accounts", "Withdraw", "Transfer", "Transaction History"], horizontal=True)

    if option == "View Accounts":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT account_id, balance FROM accounts WHERE user_id = %s", (st.session_state['user_id'],))
        accounts = cursor.fetchall()
        cursor.execute("SELECT name, dob FROM users WHERE user_id = %s", (st.session_state['user_id'],))
        user_profile = cursor.fetchone()
        conn.close()
        for acc in accounts:
            st.metric(label=f"Account ID: {acc[0]}", value=f"₹{acc[1]}")
        if user_profile:
            st.info(f"👤 Name: {user_profile[0]} | 🎂 DOB: {user_profile[1]}")

    elif option == "Withdraw":
        acc_id = st.text_input("Enter Account ID")
        amount = st.number_input("Enter Amount", min_value=0.01)
        if st.button("Withdraw", use_container_width=True):
            conn = get_db_connection()
            cursor = conn.cursor()
            if not validate_account(cursor, acc_id):
                st.error("❌ Invalid Account ID.")
                conn.close()
                return
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (acc_id,))
            balance = cursor.fetchone()
            if balance and balance[0] >= amount:
                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, acc_id))
                cursor.execute("INSERT INTO transactions (account_id, type, amount, date, details) VALUES (%s, 'Withdraw', %s, CURDATE(), %s)", (acc_id, -amount, 'Withdrawn by user'))
                conn.commit()
                st.success("✅ Withdrawal successful!")
            else:
                st.error("❌ Insufficient balance or invalid account.")
            conn.close()

    elif option == "Transfer":
        sender_acc_id = st.text_input("Enter Your Account ID")
        recipient_acc_id = st.text_input("Enter Recipient Account ID")
        amount = st.number_input("Enter Amount", min_value=0.01)

        if st.button("Transfer", use_container_width=True):
            try:
                sender_acc_id = int(sender_acc_id)
                recipient_acc_id = int(recipient_acc_id)
            except ValueError:
                st.error("❌ Account IDs must be numeric.")
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            if not validate_account(cursor, sender_acc_id) or not validate_account(cursor, recipient_acc_id):
                st.error("❌ One or both Account IDs are invalid.")
                conn.close()
                return
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (sender_acc_id,))
            sender_balance = cursor.fetchone()

            if sender_balance and sender_balance[0] >= amount:
                try:
                    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, sender_acc_id))
                    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, recipient_acc_id))

                    cursor.execute("INSERT INTO transactions (account_id, type, amount, date, details) VALUES (%s, 'Transfer', %s, CURDATE(), %s)",
                                (sender_acc_id, -amount, f'Transfer to {recipient_acc_id}'))
                    cursor.execute("INSERT INTO transactions (account_id, type, amount, date, details) VALUES (%s, 'Transfer', %s, CURDATE(), %s)",
                                (recipient_acc_id, amount, f'Received from {sender_acc_id}'))

                    conn.commit()
                    st.success("✅ Transfer successful!")
                except Exception as e:
                    st.error(f"❌ Error during transaction: {e}")
                finally:
                    conn.close()
            else:
                st.error("❌ Insufficient balance or invalid sender account.")

            conn.close()

    elif option == "Transaction History":
        period = st.selectbox("Select Time Period", ["Yesterday", "Today", "Week", "Month"])
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get account ids for the current user
        cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (st.session_state['user_id'],))
        account_ids = [row[0] for row in cursor.fetchall()]

        if not account_ids:
            st.warning("⚠️ No accounts found for this user.")
            return

        # Build the SQL query dynamically
        query = "SELECT * FROM transactions WHERE account_id IN ({})".format(",".join(["%s"] * len(account_ids)))
        
        # Add conditions based on the selected period
        if period == "Yesterday":
            query += " AND date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
        elif period == "Today":
            query += " AND date = CURDATE()"
        elif period == "Week":
            query += " AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        elif period == "Month":
            query += " AND date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        
        # Pass the account_ids as parameters for the placeholders in the query
        params = account_ids

        # Execute the query with the parameters
        cursor.execute(query, params)
        transactions = cursor.fetchall()

        conn.close()

    # Display the results
        if transactions:
            st.dataframe(transactions, use_container_width=True)
        else:
            st.warning("⚠️ No transactions found for the selected period.")

            
    if st.button("Logout", use_container_width=True):
        del st.session_state['user_id']
        del st.session_state['role']
        st.rerun()


def main():
    ensure_interest_log_table()

    # ✅ Ensure admin user is created
    create_admin_user()

    st.write("📦 Starting SmartBank...")
    conn_test = get_db_connection()
    if conn_test:
        st.success("✅ Connected to MySQL database!")
        conn_test.close()
    else:
        st.error("❌ MySQL connection failed. Please check credentials.")
        st.stop()  # Prevent app from running further if DB is unreachable


    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE transactions ADD COLUMN date DATE")
        conn.commit()
        conn.close()
    except mysql.connector.Error:
        pass  # Already exists


    st.markdown("""
        <div style='text-align: center; padding: 30px 0;'>
            <h1 class='title-text'>🏦 Welcome to SmartBank</h1>
            <h3 class='subtitle-text'>💰 Aapka Paisa, Hamara Bharosa – Safe, Secure, and Always Yours! 🔐✨</h3>
        </div>
    """, unsafe_allow_html=True)

    if 'user_id' not in st.session_state:
        if 'show_register' not in st.session_state:
            st.session_state['show_register'] = False

        if st.session_state['show_register']:
            register_user()
        else:
            login()
    else:
        if st.session_state['role'] == 'customer':
            customer_dashboard()
        elif st.session_state['role'] == 'teller':
            teller_dashboard()
        elif st.session_state['role'] == 'admin':
            admin_dashboard()


if __name__ == "__main__":
    main()
