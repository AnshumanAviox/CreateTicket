import pyodbc

# Database connection details
server = "172.31.6.34"
database = "CHILI_PROD"
username = "chiliadmin"
password = "h77pc0l0"
port = "1433"

# Connection string
conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"

try:
    # Establish connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Sample query to fetch data (Modify as per your requirement)
    query = "SELECT TOP 10 * FROM your_table_name"
    cursor.execute(query)

    # Fetch and print results
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
        print(dict(zip(columns, row)))  # Print row as dictionary

    # Close connection
    cursor.close()
    conn.close()

except Exception as e:
    print("Error:", e)
