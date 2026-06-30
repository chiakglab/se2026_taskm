import sqlite3
from app import init_db, DB

# ------------------------------
# スタッフを最初に何人か登録しておくスクリプト
# このアプリでは「スタッフを追加する画面」は作っていない
# 実行は1回だけでいい（実行するたびに同じ名前が増える）
# ------------------------------

init_db()

names = ["田中", "佐藤", "鈴木", "高橋", "伊藤"]

conn = sqlite3.connect(DB)
for name in names:
    conn.execute("INSERT INTO staff (name) VALUES (?)", (name,))
conn.commit()
conn.close()

print("スタッフを登録しました：", names)
