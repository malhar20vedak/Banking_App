import mysql.connector
import csv

# Database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password_here',
    'database': 'your_database_name'
}

# CSV file path
csv_file_path = r"relevant_file_path"  # Update path if needed

try:
    # Connect to MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Open the CSV and insert data
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            account_id = int(row['account_id'])
            user_id = int(row['user_id'])
            balance = float(row['balance'])

            cursor.execute("""
                INSERT INTO accounts (account_id, user_id, balance)
                VALUES (%s, %s, %s)
            """, (account_id, user_id, balance))

    conn.commit()
    print("✅ Account data inserted successfully.")

except mysql.connector.Error as e:
    print(f"❌ MySQL Error: {e}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        
