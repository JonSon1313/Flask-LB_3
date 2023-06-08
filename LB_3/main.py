import random
from datetime import datetime
import pytz
from flask import Flask, render_template, g,current_app
import psycopg2
from flask.cli import with_appcontext
import click
import psycopg2.extras



app = Flask(__name__)

##routs
@app.route("/dump")
def dump_entries():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rows = cursor.fetchall()
    output = ""
    for r in rows:
        debug(str(dict(r)))
        output += str(dict(r))
        output += "\n"
    return "<pre>" + output + "</pre>"

@app.route("/time")
def get_time():
    now = datetime.now().astimezone(pytz.timezone("US/Central"))
    timestring = now.strftime("%Y-%m-%d %H:%M:%S")  # format the time as an easy-to-read string
    beginning = "<html><body><h1>The time is: "
    ending = "</h1></body></html>"
    return render_template("time.html", timestring=timestring)
@app.route("/")
def hello_world():
    return "Hello, world!"  

@app.route("/random")
def pick_word():
    random_list = ['Зайцев', 'Максим', 'КІД-22']
    random_word = random.choice(random_list)
    return render_template("random.html", word=random_word)

# Database handling 
def connect_db():
    debug("Connecting to DB.")
    conn = psycopg2.connect(host="localhost", user="postgres", password="Drogba123454321", dbname="Flask", 
        cursor_factory=psycopg2.extras.DictCursor)
    return conn

def get_db():
    if "db" not in g:
        g.db = connect_db()
    return g.db
@app.teardown_appcontext
def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()
        debug("Closing DB")

@app.cli.command("initdb")
def init_db():
    """Clear existing data and create new tables."""
    conn = get_db()
    cur = conn.cursor()
    with current_app.open_resource("schema.sql") as file: 
        alltext = file.read() 
        cur.execute(alltext) 
    conn.commit()
    print("Initialized the database.")

@app.cli.command('populate')
def populate_db():
    conn = get_db()
    cur = conn.cursor()
    with current_app.open_resource("populate.sql") as file: 
        alltext = file.read() 
        cur.execute(alltext) 
    conn.commit()
    print("Populated.")

@app.route("/browse")
def browse():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rowlist = cursor.fetchall()
    return render_template('browse.html', entries=rowlist)

   
def debug(s):
    if app.config['DEBUG']:
        print(s)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
