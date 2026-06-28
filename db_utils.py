import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters from environment variables
db_params = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME'),
}

def execute_sql_query(query: str):
    conn = None
    cur = None
    try:
        # Establish a database connection
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Execute the SQL query
        cur.execute(query)

        # Fetch all results
        results = cur.fetchall()

        # Get column names from cursor description
        column_names = [desc[0] for desc in cur.description]

        # Convert results to a list of dictionaries for easier handling
        result_dicts = []
        for row in results:
            result_dicts.append(dict(zip(column_names, row)))

        return result_dicts

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()
