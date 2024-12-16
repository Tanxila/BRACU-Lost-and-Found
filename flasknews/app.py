from flask import Flask, request, jsonify, render_template
import sqlite3
import uuid
import os
from findmatch import find_matches_logic

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Test endpoint is working!"}), 200
def connect_db():
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        category TEXT,
        last_seen_location TEXT,
        date TEXT,
        photos TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    default_categories = ["Electronics", "Clothing", "Documents", "Accessories", "Others"]
    cursor.executemany("""
    INSERT OR IGNORE INTO categories (name) VALUES (?)
    """, [(category,) for category in default_categories])
    
    conn.commit()
    conn.close()

@app.route('/createPost', methods=['POST'])
def create_post():
    req_data = request.json
    post_id = uuid.uuid4().hex
    title = req_data.get('title')
    description = req_data.get('description')
    category = req_data.get('category')
    last_seen_location = req_data.get('last_seen_location')
    date = req_data.get('date')
    photos = req_data.get('photos', '')  # This can be a comma-separated list of photo URLs

    # Validate category
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories WHERE name = ?", (category,))
    valid_category = cursor.fetchone()
    if not valid_category:
        return jsonify({"error": f"Category '{category}' does not exist"}), 400

    # Insert the post
    cursor.execute("""
    INSERT INTO posts (id, title, description, category, last_seen_location, date, photos)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (post_id, title, description, category, last_seen_location, date, photos))
    conn.commit()
    conn.close()

    return jsonify({"message": "Post created successfully", "id": post_id}), 201

# categories
@app.route('/categories', methods=['GET'])
def get_categories():
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify({"categories": categories}), 200
@app.route('/getPosts', methods=['GET'])
def get_posts():
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, category, last_seen_location, date, photos FROM posts")
    posts = [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "category": row[3],
            "last_seen_location": row[4],
            "date": row[5],
            "photos": row[6]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify({"posts": posts}), 200
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/findmatch')
def findmatch_page():
    return render_template('findmatch.html')
@app.route('/findMatches', methods=['POST'])
def find_matches():
    req_data = request.json  # Input data from frontend
    results = find_matches_logic(req_data)  # Call function from findmatch.py
    return jsonify(results)


if __name__ == '__main__':
    connect_db()
    app.run(debug=True, port=1037)
