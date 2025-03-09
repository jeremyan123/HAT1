'''Web app'''
#IMPORTS
import sqlite3
import smtplib
import ssl
import random
from flask import Flask, request, render_template, session, redirect, url_for
app = Flask(__name__)
# secret key is used to encrypt session storage data
app.secret_key = '6MT7DbpbBnGeOKC0HzthJVngnpBmne7v'

@app.route('/', methods=['POST'])
def post():
    '''handling the login/signup form requests'''
    # creating an array of users from data.db
    users = sqlite3.connect('database/data.db').cursor().execute("SELECT * FROM users").fetchall()
    sqlite3.connect('database/data.db').close()
    # testing whether the user is logging in or signing up (Continue is used for login and create account is signup)
    if request.form['button']=="CONTINUE":
        # getting the values from the login form
        username = request.form['username']
        password = request.form['password']
        # iterating through each row/user in the array previously defined
        for x in users:
            # testing if the username matches that of the database 
            if x[1].lower()==username.lower():
                # testing if the password matches
                if x[2]==password:
                    # setting a variable in the user's session storage to be used when determining if the user is logged in or not
                    session['logged_in'] = True
                    # check if the account is the defined admin account
                    if username=="jeremy":
                        # add a variable in session storage telling the server that the logged in account is an administrator
                        session['admin']=True
                # send the user to the index page
                return redirect('/')
            # if the username or password is wrong, refresh the page
        return render_template("login.html", error="Invalid Username or Password")
    # signup handling
    if request.form['button']=="CREATE ACCOUNT":
        # get the values from signup form
        username = request.form['username']
        password = request.form['password']
        email=request.form['email']
        # if the inputted username has no length (is blank), refresh the page
        if len(str(username))==0:
            return render_template("signup.html", error="Username Field is Blank")
        invalid = False # local variable used to check if the username already exists
        # iterate through the users array to test if the username already exists
        for i in users:
            if i[1].lower()==username.lower():
                invalid=True
        if not invalid:
            #establishing the email 'server' used to send users their verification code
            with smtplib.SMTP_SSL("smtp.gmail.com", 465,
                                  context=ssl.create_default_context()) as server:
                server.login("randomguy321321321321@gmail.com", "uqyn gtdg kimp tvxj") # logging into the gmail account
                code=random.randint(1000, 9999) # make a random verification code
                message = "Subject: Verification Code\n"+ str(code) # define the message used in the email
                server.sendmail("randomguy321321321321@gmail.com", email, message) # sending the email
                #defining temporary session variables to use when verifying email
                session['email']=email 
                session['username']=username
                session['password']=password
                session['code']=code
                return redirect(url_for('verification')) #send the user to the verifcation page
        return render_template('signup.html', error="Username is already in use") #if the username is invalid, refresh the page


# --- Rendering the respective page when the user goes to a location on the website ---
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
    '''delete session cookies and redirect to login.html'''
    #deleting the session cookies
    session.pop('logged_in', None)
    session.pop('admin', None)
    return render_template('login.html')

@app.route('/verification', methods=['GET'])
def verification():
    '''redirect to verification.html'''
    return render_template('verification.html')

@app.route('/verification', methods=['POST'])
def handleverification():
    '''handle posts to verification.html'''
    # test if the inputted code is correct
    if request.form['code']==str(session['code']):
        # adding the user to the database
        insertsql("INSERT INTO users(username, password, email) VALUES (?, ?, ?)",
                  (session['username'], session['password'], session['email']))
        # deleting the unnecessary session cookies
        session.pop('username', None)
        session.pop('password', None)
        session.pop('email', None)
        session.pop('code', None)
        return redirect(url_for('login')) #send the user to the login page where they can sign into the account they made
    return render_template('verification.html', error="Invalid verification code") # if the code is wrong, refresh the page


@app.route('/place', methods=['GET'])
def showplace():
    '''redirect to place.html'''
    #defining SQL queries used in the return statement to reduce the length of code
    query = f"SELECT * FROM catalogue WHERE place_id={request.args.get('place_id')}"
    reviews = f"SELECT * FROM reviews WHERE review_id={request.args.get('place_id')}"
    # show place.html with arguments containing the restaurant's data
    return render_template('place.html',
                           catalogue=sqlite3.connect('database/data.db').cursor()
                           .execute(query).fetchall(),
                            images=sqlite3.connect('database/data.db').cursor()
                                .execute("SELECT * FROM images").fetchall(),
                            reviews=sqlite3.connect('database/data.db').cursor()
                                .execute(reviews).fetchall(),
                           close=sqlite3.connect('database/data.db').close())

@app.route('/postplace', methods=['GET'])
def postscreen():
    '''redirect to postplace.html'''
    return render_template('postplace.html')

@app.route('/category', methods=['GET'])
def showcategory():
    '''get the category's relevant info and return it'''
    # show category.html with the respective category's data
    return render_template('category.html',
                           category=request.args.get("category"),
                           catalogue=sqlite3.connect('database/data.db').cursor().execute(
                               "SELECT * FROM catalogue"),
                            images=sqlite3.connect('database/data.db').cursor()
                                .execute("SELECT * FROM images").fetchall(),
                           close=sqlite3.connect('database/data.db').close())

# a function for administrator accounts, simplifying the process of adding data to data.db
@app.route('/postplace', methods=['POST'])
def postdata():
    '''get the info from the post form and update the database to include it. refresh the page'''
    con = sqlite3.connect('database/data.db')
    cur = con.cursor()
    # adding the restaurant to "catalogue" in data.db
    cur.execute("INSERT INTO catalogue(name, category,"
                "coordx, coordy, address, open_hours, website, phone_number, rating"
                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (request.form['name'], request.form['category'],
                float(request.form['coordx']), float(request.form['coordy']),
                request.form['address'], request.form['open_hours'],
                request.form['website'], request.form['phone_number'],
                request.form['rating']))
    # adding the restaurant's reviews to "reviews" in data.db
    cur.execute("INSERT INTO reviews(review1, review2) VALUES (?, ?)",
                (request.form['review1'], request.form['review2']))
    # adding the restaurant's images to "images" in data.db
    cur.execute("INSERT INTO images(image1, image2, image3) VALUES (?, ?, ?)",
                (request.form['image1'], request.form['image2'], request.form['image3']))
    con.commit()
    con.close()
    return render_template("postplace.html")

@app.route('/', methods=['GET'])
def home():
    '''redirect to index.html if logged in and login.html if not'''
    # using a try statement to test if the user is logged in or not
    try:
        # displaying index.html with arguments containing the data of all restaurants
        return render_template('index.html',
                               signed_in=session['logged_in'], # <- the part that will be caught if the user is not logged in
                               view=request.args.get("view"),
                               catalogue=sqlite3.connect('database/data.db').cursor()
                                .execute("SELECT * FROM catalogue").fetchall(),
                                images=sqlite3.connect('database/data.db').cursor()
                                .execute("SELECT * FROM images").fetchall(),
                                close=sqlite3.connect('database/data.db').close())
    except KeyError: # if the user isnt logged in
        return render_template('login.html')


def insertsql(query, values):
    '''function to simplify sql queries'''
    con = sqlite3.connect('database/data.db')
    cur = con.cursor()
    # executing the inputted query
    cur.execute(query, values)
    con.commit()
    con.close()

if __name__ == '__main__':
    app.run(debug=True)
