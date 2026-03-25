import os
from flask import Flask, render_template, request, redirect
from db import get_db, init_db, seed_data
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../frontend/templates"),
    static_folder=os.path.join(BASE_DIR, "../frontend/static")
)

# Initialize DB
init_db()
seed_data()


# 🟢 HOME — USERS
@app.route("/")
def home():
    users = requests.get("https://jsonplaceholder.typicode.com/users").json()

    conn = get_db()
    posts = conn.execute("SELECT * FROM posts").fetchall()
    conn.close()

    user_data = []

    for user in users:
        user_posts = [p for p in posts if p["user_id"] == user["id"]]

        image_id = user_posts[0]["id"] if user_posts else 1

        user_data.append({
            "user": user,
            "image_id": image_id
        })

    return render_template("index.html", user_data=user_data)



# 🟡 USER POSTS (FIXED ROUTE)
@app.route("/user/<int:user_id>")
def user_posts(user_id):
    import requests

    conn = get_db()
    posts = conn.execute(
        "SELECT * FROM posts WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()

    # fetch user details
    user = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}").json()

    return render_template("user_posts.html", posts=posts, user=user)


# 🔴 POST DETAIL
@app.route("/post/<int:post_id>")
def post_detail(post_id):
    conn = get_db()

    post = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    comments = conn.execute("SELECT * FROM comments WHERE post_id=?", (post_id,)).fetchall()

    conn.close()

    return render_template("post.html", post=post, comments=comments)


# ➕ CREATE POST (FIXED)
@app.route("/create/<int:user_id>", methods=["GET", "POST"])
def create_post(user_id):
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        conn = get_db()
        conn.execute(
            "INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)",
            (user_id, title, body)
        )
        conn.commit()
        conn.close()

        return redirect(f"/user/{user_id}")

    return render_template("create.html", user_id=user_id)


if __name__ == "__main__":
    app.run(debug=True,
            host='0.0.0.0',
            port=5000)