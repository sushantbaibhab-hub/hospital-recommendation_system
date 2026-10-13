from flask import Flask, render_template_string, request
import sqlite3

app = Flask(__name__)
DB_NAME = "hospitals.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            speciality TEXT NOT NULL,
            budget TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM hospitals"
    ).fetchone()[0]

    if count == 0:
        hospitals = [
            ("Rajpura General Hospital", "Rajpura", "General", "Low",
             "Rajpura, Punjab"),
            ("Patiala Heart Centre", "Patiala", "Heart", "High",
             "Patiala, Punjab"),
            ("Chandigarh Eye Hospital", "Chandigarh", "Eye", "Medium",
             "Chandigarh"),
            ("Mohali Bone Care", "Mohali", "Bone", "Medium",
             "Mohali, Punjab"),
            ("Zirakpur General Hospital", "Zirakpur", "General", "Low",
             "Zirakpur, Punjab")
        ]
        conn.executemany("""
            INSERT INTO hospitals
            (name, city, speciality, budget, address)
            VALUES (?, ?, ?, ?, ?)
        """, hospitals)

    conn.commit()
    conn.close()


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hospital Recommendation System</title>
<style>
body { font-family: Arial; background: #eef5fb; margin: 0; color: #222; }
header { background: #087e8b; color: white; text-align: center; padding: 24px; }
main { max-width: 650px; margin: 30px auto; padding: 25px; background: white;
       border-radius: 12px; box-shadow: 0 3px 12px #ccd; }
label { display: block; margin-top: 15px; font-weight: bold; }
input, select, button { width: 100%; padding: 11px; margin-top: 7px;
                        box-sizing: border-box; }
button { margin-top: 22px; background: #087e8b; color: white;
         border: 0; border-radius: 6px; cursor: pointer; }
.result { background: #e0f6e8; padding: 15px; margin-top: 20px; }
.map { display: inline-block; margin-top: 10px; }
</style>
</head>
<body>
<header>
<h1>🏥 Hospital Recommendation System</h1>
<p>Find hospitals by city, speciality and budget</p>
</header>
<main>
<h2>Find a Hospital</h2>
<form method="POST">
<label>Patient name</label>
<input name="patient" required>
<label>City</label>
<select name="city" required>
<option value="">Choose city</option>
{% for city in cities %}
<option>{{ city }}</option>
{% endfor %}
</select>
<label>Health problem</label>
<select name="speciality" required>
<option value="">Choose speciality</option>
{% for s in ["General", "Heart", "Kidney", "Bone", "Skin", "Eye"] %}
<option>{{ s }}</option>
{% endfor %}
</select>
<label>Budget</label>
<select name="budget" required>
<option value="">Choose budget</option>
<option>Low</option><option>Medium</option><option>High</option>
</select>
<button type="submit">Recommend Hospital</button>
</form>

{% if results is not none %}
<div class="result">
<h2>Recommendation Results</h2>
<p>Patient: {{ patient }}</p>
{% if results %}
{% for h in results %}
<hr>
<p><b>{{ h[0] }}</b></p>
<p>City: {{ h[1] }} | Speciality: {{ h[2] }} | Budget: {{ h[3] }}</p>
<p>Address: {{ h[4] }}</p>
<a class="map" href="https://www.google.com/maps/search/?api=1&query={{ h[4] | urlencode }}"
target="_blank" rel="noopener">View on Google Maps</a>
{% endfor %}
{% else %}
<p>No matching hospital found in our sample database. Try another city or budget.</p>
{% endif %}
<p><small>Demo project only. Hospital details and suitability must be verified before visiting.</small></p>
</div>
{% endif %}
</main>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    cities = ["Rajpura", "Patiala", "Chandigarh", "Mohali", "Zirakpur"]
    results = None
    patient = ""

    if request.method == "POST":
        patient = request.form["patient"].strip()
        city = request.form["city"]
        speciality = request.form["speciality"]
        budget = request.form["budget"]

        conn = sqlite3.connect(DB_NAME)
        rows = conn.execute("""
            SELECT name, city, speciality, budget, address
            FROM hospitals
            WHERE city = ? AND (speciality = ? OR speciality = 'General')
              AND budget = ?
        """, (city, speciality, budget)).fetchall()
        conn.close()

        results = rows

    return render_template_string(
        PAGE, cities=cities, results=results, patient=patient
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)