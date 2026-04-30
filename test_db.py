import psycopg2
try:
    conn = psycopg2.connect(
        dbname="ope_db",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    print("Connection successful")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    try:
        print(f"Hex: {e.args[0].encode('latin-1').hex()}")
    except:
        pass
