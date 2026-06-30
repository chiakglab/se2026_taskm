import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
DB = "data.db"


# ------------------------------
# データベースの準備
# 起動時に1回だけ実行される
# テーブルがなければ作る（あれば何もしない）
# staff と tasks、2つのテーブルがある
# tasks の assigned_to が staff の id を参照する
# ------------------------------
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            assigned_to INTEGER NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT '未着手',
            FOREIGN KEY (assigned_to) REFERENCES staff (id)
        )
    """)
    conn.commit()
    conn.close()


# ------------------------------
# ルート 1：タスク一覧 (Read)
# GET /tasks
# tasks と staff を JOIN して、担当者の名前も一緒に表示する
# 締切が近い順に並べる
# ------------------------------
@app.route("/tasks")
def show_tasks():
    conn = sqlite3.connect(DB)
    tasks = conn.execute("""
        SELECT tasks.id, tasks.title, staff.name, tasks.deadline, tasks.status
        FROM tasks
        JOIN staff ON tasks.assigned_to = staff.id
        ORDER BY tasks.deadline
    """).fetchall()
    conn.close()
    return render_template("tasks.html", tasks=tasks)


# ------------------------------
# ルート 2：タスク作成 (Create)
# GET  /tasks/new → 空のフォームを表示する（担当者の選択肢も渡す）
# POST /tasks/new → フォームの内容をDBに保存する
# ------------------------------
@app.route("/tasks/new", methods=["GET", "POST"])
def new_task():
    conn = sqlite3.connect(DB)

    if request.method == "POST":
        title = request.form["title"]
        assigned_to = request.form["assigned_to"]
        deadline = request.form["deadline"]
        conn.execute(
            "INSERT INTO tasks (title, assigned_to, deadline) VALUES (?, ?, ?)",
            (title, assigned_to, deadline),
        )
        conn.commit()
        conn.close()
        return redirect("/tasks")

    staff_list = conn.execute("SELECT id, name FROM staff").fetchall()
    conn.close()
    return render_template("form.html", task=None, staff_list=staff_list)


# ------------------------------
# ルート 3：タスク編集 (Update)
# GET  /tasks/<id>/edit → 既存データを入れたフォームを表示する
# POST /tasks/<id>/edit → 変更内容をDBに反映する
# ------------------------------
@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    conn = sqlite3.connect(DB)

    if request.method == "POST":
        title = request.form["title"]
        assigned_to = request.form["assigned_to"]
        deadline = request.form["deadline"]
        conn.execute(
            "UPDATE tasks SET title = ?, assigned_to = ?, deadline = ? WHERE id = ?",
            (title, assigned_to, deadline, task_id),
        )
        conn.commit()
        conn.close()
        return redirect("/tasks")

    task = conn.execute(
        "SELECT id, title, assigned_to, deadline FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    staff_list = conn.execute("SELECT id, name FROM staff").fetchall()
    conn.close()
    return render_template("form.html", task=task, staff_list=staff_list)


# ------------------------------
# ルート 4：ステータス更新
# POST /tasks/<id>/status
# 一覧画面のボタンから直接呼ばれる
# 未着手 → 進行中 → 完了 の順に進む（簡易ロジック）
# ------------------------------
@app.route("/tasks/<int:task_id>/status", methods=["POST"])
def update_status(task_id):
    conn = sqlite3.connect(DB)
    current = conn.execute(
        "SELECT status FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()[0]

    next_status = {
        "未着手": "進行中",
        "進行中": "完了",
        "完了": "未着手",
    }[current]

    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (next_status, task_id))
    conn.commit()
    conn.close()
    return redirect("/tasks")


# ------------------------------
# ルート 5：タスク削除 (Delete)
# POST /tasks/<id>/delete
# 削除は「状態を変える操作」なので、GETではなくPOSTを使う
# ------------------------------
@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/tasks")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
