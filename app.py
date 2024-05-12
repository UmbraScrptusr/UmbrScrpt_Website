"""
Author: Franciszek Czajkowski
Start-date: 01/05/24
Last modified: 10/05/24
Description:
Main UmbraScript Website
"""
import os
from flask import Flask, session, render_template, request, redirect, g, url_for
import sqlite3

logins = {
    'admin':'admin'
}
id_in_list = 2

db_name = "logins.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
conn.execute("DROP TABLE IF EXISTS logins")

def create_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")


def update():
    cursor.execute("PRAGMA foreign_keys=off")
    cursor.execute("BEGIN TRANSACTION")
    for i, login in logins.items():
        username = login['username']
        password = login['password']
        cursor.execute("INSERT OR REPLACE INTO logins (id, username, password) VALUES (?, ?, ?)",
                       (i, username, password))
    cursor.execute("COMMIT")
    cursor.execute("PRAGMA foreign_keys=on")
    print("Database updated successfully.")
def select_all():
    cursor.execute('SELECT * FROM logins')
    rows = cursor.fetchall()
    for row in rows:
        print(row)


try:
    create_table()
    update()
    select_all()
except sqlite3.Error as e:
    print("SQLite error:", e)
finally:
    conn.close()

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/main", methods=['GET', 'POST'])
@app.route("/main", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # Processing form submission
        session.pop('user', None)
        username = request.form['username']
        username.lower()
        password = request.form['password']

        # Check if the username exists in logins and the password matches
        if username in logins and password == logins[username]:
                session['user'] = username
                return redirect(url_for('protected'))  # Redirect to the protected route after successful login

    return render_template('main.html')  # Render the login page template


@app.route('/admin_panel')
def admin_panel():
    if g.user:
        return render_template('admin_panel.html', user=session['user'])
    return redirect(url_for('main'))


@app.route("/protected")
def protected():
    if g.user:
        print("Redirecting to protected route")
        return render_template('protected.html', user=session['user'])
    print("User is not authenticated, redirecting to main route")
    return redirect(url_for('main'))


@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    global id_in_list
    if request.method == 'POST':
        session.pop('user', None)

        if request.form['username'] not in logins:
            logins[id_in_list] = {'username': request.form['username'], 'password': request.form['password']}
            id_in_list += 1
            try:
                create_table()
                update()
                select_all()
            except sqlite3.Error as e:
                print("SQLite error:", e)

            print(logins)
            return redirect(url_for('main'))

    return render_template('sign_up.html')


@app.route("/")
def index():
    return render_template('index.html')


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


if __name__ == '__main__':
    app.run(debug=True)
