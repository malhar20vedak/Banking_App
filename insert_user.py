import csv
import bcrypt
import mysql.connector

# Function to connect to the database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Your MySQL username
        password="Aman@6006",  # Your MySQL password
        database="bank_nndb"
    )

# Read CSV and insert users into the database
def insert_users_from_csv(csv_file_path):
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            name = row['name']
            username = row['username']
            password = row['password']
            role = row['role']
            phone = row['phone']
            dob = row['dob']
            address = row['address']
            uid = row['uid']

            # Hash the password using bcrypt
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insert into users table
            cursor.execute("""
                INSERT INTO users (name, username, password, role, phone, dob, address, uid) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, username, hashed_password, role, phone, dob, address, uid))

            print(f"Inserted user {username}")

    conn.commit()
    cursor.close()
    conn.close()

# Provide the path to your CSV file
csv_file_path = r"C:\Users\Aman Kumar\Downloads\Users_Data_Cleaned.csv"  # Make sure this path is correct
insert_users_from_csv(csv_file_path)
