'''Web app'''
import sqlite3
from flask import Flask, request, render_template, session, redirect
app = Flask(__name__)
app.secret_key = '6MT7DbpbBnGeOKC0HzthJVngnpBmne7v'

@app.route('/', methods=['POST'])
def post():
    '''handling the login requests'''
    users = sqlite3.connect('database/data.db').cursor().execute("SELECT * FROM users").fetchall()
    sqlite3.connect('database/data.db').close()
    if request.form['button']=="CONTINUE":
        username = request.form['username']
        password = request.form['password']
        if username.lower()=="log":
            print(users)
        logged_in = False
        for x in users:
            if x[1].lower()==username.lower():
                if x[2]==password:
                    print(f"User logged in as {username}")
                    session['logged_in'] = True
                    if username=="jeremy":
                        session['admin']=True
                return redirect('/')
        if logged_in is False:
            return render_template("login.html", error="Invalid Username or Password")
    elif request.form['button']=="CREATE ACCOUNT":
        username = request.form['username']
        password = request.form['password']
        invalid = False
        for i in users:
            if i[1].lower()==username.lower():
                invalid=True
        if invalid is False:
            con = sqlite3.connect('database/data.db')
            cur = con.cursor()
            cur.execute("INSERT INTO users(username, password, email) VALUES (?, ?, ?)"
                        , (username, password, "testemail"))
            con.commit()
            con.close()

            return render_template('verification.html')
        return render_template('signup.html', error="Username is already in use")


@app.route('/login', methods=['GET'])
def login():
    '''redirect to login.html'''
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup():
    '''redirect to signup.html'''
    return render_template('signup.html')

@app.route('/logout')
def logout():
    '''redirect delete session cookies and redirect to login.html'''
    session.pop('logged_in', None)
    session.pop('admin', None)
    return render_template('login.html')

@app.route('/verification')
def verification():
    '''redirect to verification.html'''
    return render_template('verification.html')

@app.route('/about', methods=['GET'])
def aboutpage():
    '''redirect to about.html'''
    return render_template('about.html')

@app.route('/place', methods=['GET'])
def showplace():
    '''redirect to place.html'''
    query = f"SELECT * FROM catalogue WHERE place_id={request.args.get('place_id')}"
    return render_template('place.html',
                           catalogue=sqlite3.connect('database/data.db').cursor()
                           .execute(query).fetchall(),
                           close=sqlite3.connect('database/data.db').close())

@app.route('/postplace', methods=['GET'])
def postscreen():
    '''redirect to postplace.html'''
    return render_template('postplace.html')

@app.route('/category', methods=['GET'])
def showcategory():
    '''get the category's relevant info and return it'''
    return render_template('category.html',
                           category=request.args.get("category"),
                           catalogue=sqlite3.connect('database/data.db').cursor().execute(
                               "SELECT * FROM catalogue"),
                           close=sqlite3.connect('database/data.db').close())

@app.route('/postplace', methods=['POST'])
def postdata():
    '''get the info from the post form and update the database to include it. refresh the page'''
    place_id = int(request.form['place_id'])
    name = request.form['name']
    category = request.form['category']
    coordx = float(request.form['coordx'])
    coordy = float(request.form['coordy'])
    address = request.form['address']
    open_hours = request.form['open_hours']
    website = request.form['website']
    phone_number = request.form['phone_number']
    rating = request.form['rating']
    con = sqlite3.connect('database/data.db')
    cur = con.cursor()
    cur.execute("INSERT INTO catalogue(place_id, name, category,"
                "coordx, coordy, address, open_hours, website, phone_number, rating"
                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (place_id, name, category, coordx, coordy,
                 address, open_hours, website, phone_number, rating))
    con.commit()
    con.close()
    return render_template("postplace.html")

@app.route('/', methods=['GET'])
def home():
    '''redirect to index.html if logged in and login.html if not'''
    try:
        return render_template('index.html', 
                               signed_in=session['logged_in'], 
                               view=request.args.get("view"), 
                               catalogue=sqlite3.connect('database/data.db').cursor()
                                .execute("SELECT * FROM catalogue").fetchall(),
                                close=sqlite3.connect('database/data.db').close())
    except KeyError:
        return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
