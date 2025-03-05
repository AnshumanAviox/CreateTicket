import pyodbc
import datetime
from datetime import timedelta


def insert_dummy_data(process_id, ticket_id):
    # Connection string with your provided credentials
    conn_str = (
        "DRIVER={SQL Server};"
        "SERVER=172.31.6.34,1433;"
        "DATABASE=CHILI_PROD;"
        "UID=chiliadmin;"
        "PWD=h77pc0l0;"
    )

    try:
        # Establish connection
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Generate test data
        current_time = datetime.datetime.now()
        test_data = {
            'process_id': process_id,
            'ticket_id': ticket_id,
            'trip_start_time': current_time,
            'trip_end_time': current_time + timedelta(hours=1),
            'wait_start_time': current_time + timedelta(minutes=15),
            'wait_end_time': current_time + timedelta(minutes=30),
            'pickup_photo': b'dummy_pickup_photo_data',
            'drop_photo': b'dummy_drop_photo_data',
            'signature': b'dummy_signature_data',
            'notes': f'Test invoice entry at {current_time}'
        }

        # Insert query
        insert_query = """
        INSERT INTO INVOICE_DETAILS (
            process_id, ticket_id, trip_start_time, trip_end_time,
            wait_start_time, wait_end_time, pickup_photo, drop_photo,
            signature, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Execute insert
        cursor.execute(insert_query, (
            test_data['process_id'],
            test_data['ticket_id'],
            test_data['trip_start_time'],
            test_data['trip_end_time'],
            test_data['wait_start_time'],
            test_data['wait_end_time'],
            test_data['pickup_photo'],
            test_data['drop_photo'],
            test_data['signature'],
            test_data['notes']
        ))

        # Commit the transaction
        conn.commit()
        print(f"Test data inserted successfully! Process ID: {process_id}, Ticket ID: {ticket_id}")

    except pyodbc.Error as e:
        print(f"Database error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


def create_test_table():
    # Connection string with your provided credentials
    conn_str = (
        "DRIVER={SQL Server};"
        "SERVER=172.31.6.34,1433;"
        "DATABASE=CHILI_PROD;"
        "UID=chiliadmin;"
        "PWD=h77pc0l0;"
    )

    try:
        # Establish connection
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Create the INVOICE_DETAILS table
        create_table_query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'INVOICE_DETAILS')
        CREATE TABLE INVOICE_DETAILS (
            id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
            process_id VARCHAR(255) NOT NULL,
            ticket_id VARCHAR(255) NOT NULL,
            trip_start_time DATETIME2(7) NOT NULL,
            trip_end_time DATETIME2(7) NOT NULL,
            wait_start_time DATETIME2(7) NULL,
            wait_end_time DATETIME2(7) NULL,
            pickup_photo VARBINARY(MAX) NOT NULL,
            drop_photo VARBINARY(MAX) NOT NULL,
            signature VARBINARY(MAX) NOT NULL,
            notes TEXT NULL
        )
        """
        cursor.execute(create_table_query)

        # Insert test data
        current_time = datetime.datetime.now()
        test_data = {
            'process_id': 'PROC_001',
            'ticket_id': 'TICKET_001',
            'trip_start_time': current_time,
            'trip_end_time': current_time + timedelta(hours=1),
            'wait_start_time': current_time + timedelta(minutes=15),
            'wait_end_time': current_time + timedelta(minutes=30),
            'pickup_photo': b'dummy_pickup_photo_data',  # Dummy binary data
            'drop_photo': b'dummy_drop_photo_data',      # Dummy binary data
            'signature': b'dummy_signature_data',        # Dummy binary data
            'notes': 'Test invoice entry'
        }

        # Insert query
        insert_query = """
        INSERT INTO INVOICE_DETAILS (
            process_id, ticket_id, trip_start_time, trip_end_time,
            wait_start_time, wait_end_time, pickup_photo, drop_photo,
            signature, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Execute insert
        cursor.execute(insert_query, (
            test_data['process_id'],
            test_data['ticket_id'],
            test_data['trip_start_time'],
            test_data['trip_end_time'],
            test_data['wait_start_time'],
            test_data['wait_end_time'],
            test_data['pickup_photo'],
            test_data['drop_photo'],
            test_data['signature'],
            test_data['notes']
        ))

        # Commit the transaction
        conn.commit()
        print("Test data inserted successfully!")

        # Verify the insertion
        cursor.execute("SELECT * FROM INVOICE_DETAILS")
        row = cursor.fetchone()
        if row:
            print("\nInserted row details:")
            print(f"ID: {row.id}")
            print(f"Process ID: {row.process_id}")
            print(f"Ticket ID: {row.ticket_id}")
            print(f"Trip Start Time: {row.trip_start_time}")
            print(f"Trip End Time: {row.trip_end_time}")

    except pyodbc.Error as e:
        print(f"Database error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    create_test_table() 