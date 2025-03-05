import pandas as pd
import sqlite3  # Change this if using another database (e.g., cx_Oracle for Oracle)

# Database connection - Change accordingly for your DB
conn = sqlite3.connect("your_database.db")  # Replace with actual database connection

# SQL query from the file
sql_query = """
SET SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS';

SELECT TO_CHAR(net_report.report_date, 'YYYY-MM-DD HH24:MI:SS') AS NET_DATE,
       net_report.ctm_host_name,
       net_report.data_fname,
       net_report.node_id
FROM your_schema.net_report
WHERE net_report.report_date BETWEEN '2024-09-01 00:00:00' AND '2024-09-30 23:59:00'
ORDER BY net_report.net_date;
"""  # Modify schema and table names as required

# Fetch data into a pandas DataFrame
df = pd.read_sql_query(sql_query, conn)

# Save to CSV
csv_filename = "net_report_data.csv"
df.to_csv(csv_filename, index=False)

print(f"Data saved to {csv_filename}")

# Close the database connection
conn.close()
