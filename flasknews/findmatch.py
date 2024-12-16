import sqlite3

def find_matches_logic(req_data):
    """
    Logic to find matches based on title, description, and location.

    Args:
        req_data (dict): Input data containing title, description, and location.

    Returns:
        dict: Matches found or a message indicating no matches.
    """
    title = req_data.get('title', '').lower()
    description = req_data.get('description', '').lower()
    location = req_data.get('last_seen_location', '').lower()

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

    matches = []

    for post in posts:
        # Check for keyword matches in title and description
        title_match = title in post["title"].lower()
        description_match = description in post["description"].lower()
        # Check for location match
        location_match = location in post["last_seen_location"].lower()

        # If any of these match, consider it a potential match
        if title_match or description_match or location_match:
            matches.append(post)

    if matches:
        return {"matches": matches}
    else:
        return {"message": "No matching items found"}
