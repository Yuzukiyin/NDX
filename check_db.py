import sqlite3

# 检查本地根目录的数据库
print("=" * 50)
print("检查 ndx_users.db")
print("=" * 50)
conn = sqlite3.connect('ndx_users.db')
c = conn.cursor()

# 查看所有表
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f"\n所有表: {[t[0] for t in tables]}")

# 如果有users表,查看内容
if any(t[0] == 'users' for t in tables):
    users = c.execute("SELECT id, email, username, is_active FROM users").fetchall()
    print(f"\nUsers表内容 ({len(users)}条记录):")
    for user in users:
        print(f"  ID={user[0]}, Email={user[1]}, Username={user[2]}, Active={user[3]}")
else:
    print("\n⚠️ 没有users表!")

# 如果有transactions表,查看数量
if any(t[0] == 'transactions' for t in tables):
    count = c.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    print(f"\nTransactions表: {count}条记录")

conn.close()

# 检查backend目录的数据库
print("\n" + "=" * 50)
print("检查 Web/backend/ndx_users.db")
print("=" * 50)
conn2 = sqlite3.connect('Web/backend/ndx_users.db')
c2 = conn2.cursor()

tables2 = c2.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f"\n所有表: {[t[0] for t in tables2]}")

if any(t[0] == 'users' for t in tables2):
    users2 = c2.execute("SELECT id, email, username, is_active FROM users").fetchall()
    print(f"\nUsers表内容 ({len(users2)}条记录):")
    for user in users2:
        print(f"  ID={user[0]}, Email={user[1]}, Username={user[2]}, Active={user[3]}")
else:
    print("\n⚠️ 没有users表!")

conn2.close()
