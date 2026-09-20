import mysql.connector

try:
    print("Connecting to MySQL...")
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="WarAnshu1!",  # Testing if "root" is your password
        database="pandeyji_eatery"  # The database name used in the chatbot project [1]
    )
    if connection.is_connected():
        print("\n🎉 SUCCESS! Your database connection works perfectly!")
        connection.close()

except mysql.connector.Error as err:
    print("\n❌ CONNECTION FAILED!")
    print(f"Error details: {err}")