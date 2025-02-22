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

    # Define the Ticket_ID to search
    ticket_id = '070508001'

    # SQL Query
    query = """
    SELECT 
        [Billing_ID], [Ticket_ID], [Customer_ID], [Called], [Pickup_Date], [Vehicle_Type],
        [Rate_Type], [Notes], [PO], [Pieces], [Skids], [Weight], [COD], 
        [From_Company], [From_Contact], [From_Address_1], [From_Address_2], 
        [From_City], [From_State], [From_Zip], [From_Phone], [From_Alt_Phone], 
        [To_Company], [To_Contact], [To_Address_1], [To_Address_2], 
        [To_City], [To_State], [To_Zip], [To_Phone], [To_Alt_Phone]
    FROM [dbo].[INVOICE_TABLE]
    WHERE Ticket_ID = ?;
    """

    # Execute query
    cursor.execute(query, (ticket_id,))

    # Fetch and print data
    columns = [column[0] for column in cursor.description]
    results = cursor.fetchall()

    if results:
        print("Query Result:")
        for row in results:
            print(dict(zip(columns, row)))
    else:
        print("No records found for Ticket_ID:", ticket_id)

    # Close connection
    cursor.close()
    conn.close()

except Exception as e:
    print("Error:", e)
