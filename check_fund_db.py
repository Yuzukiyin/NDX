import sqlite3

conn = sqlite3.connect('fund.db')
cursor = conn.cursor()

# 获取transactions表结构
cursor.execute("PRAGMA table_info(transactions)")
columns = cursor.fetchall()
print("transactions表结构:")
for col in columns:
    print(f"  {col[1]} {col[2]}")

conn.close()
