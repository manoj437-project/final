import psycopg2

conn = psycopg2.connect('postgresql://postgres:manoj@localhost:5432/edumentor')
cur = conn.cursor()

cur.execute("ALTER TABLE daily_topics ADD COLUMN IF NOT EXISTS due_date VARCHAR;")
cur.execute("ALTER TABLE daily_topics ADD COLUMN IF NOT EXISTS due_time VARCHAR;")

conn.commit()
cur.close()
conn.close()
print("SUCCESS: Columns due_date and due_time added to daily_topics table.")
