from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Secret Key"

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'earth eagle'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'cruddb'

mysql = MySQL(app)


def check_table(table_name):
    cursor = mysql.connection.cursor()
    cursor.execute(f'''
        SHOW TABLES LIKE '{table_name}'
    ''')
    result = cursor.fetchone()
    if result:
        return True
    elif table_name == 'accounts':
        cursor.execute('''
            CREATE TABLE accounts(
                    LoginID INT PRIMARY KEY AUTO_INCREMENT,
                    Username VARCHAR(15),
                    Password VARCHAR (15),
                    Email VARCHAR (40)
                );
        ''')
        mysql.connection.commit()
        cursor.close()
        return True
    elif table_name == 'conversion':
        cursor.execute('''
            CREATE TABLE conversion(
                AppID BIGINT PRIMARY KEY,
                firstName VARCHAR(20),
                lastName VARCHAR(20),
                contact BIGINT,
                mouza VARCHAR(20),
                khata VARCHAR(20),
                plot VARCHAR(20),
                tarea DECIMAL(10,5),
                payment1  DECIMAL(10,3),
                payment2 DECIMAL(10,3),
                tID VARCHAR(20),
                olr VARCHAR(20),
                doa DATE
            );
        ''')
        mysql.connection.commit()
        cursor.close()
        return True
    elif table_name == 'review':
        cursor.execute('''
            CREATE TABLE review(
                CustomerID INT PRIMARY KEY AUTO_INCREMENT,
                LoginID INT,
                Username VARCHAR(25),
                name VARCHAR(30),
                contact BIGINT,
                Email VARCHAR (40),
                comment VARCHAR(500),
                rating INT,
                currentDate DATE
)               ;
        ''')
        mysql.connection.commit()
        cursor.close()
        return True
    else:
        return "Unable to Create Table"


@app.route('/', methods=['GET', 'POST'])
def login():
    result = check_table('accounts')
    if result:
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f'''
                    SELECT * FROM accounts 
                    WHERE Username = '{username}' AND Password = '{password}'
                ''', )
            account = cursor.fetchone()
            print(account)
            # IF account exists
            if account:
                session['loggedin'] = True
                session['id'] = account['LoginID']
                session['Username'] = account['Username']
                cursor.close()
                return redirect(url_for('home'))
            else:
                msg = "Incorrect username/password"
        return render_template('login.html', msg=msg)


@app.route('/home')
def home():
    # Check if user is loggedin
    print(session)
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['Username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    result = check_table('accounts')
    if result:
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f'''
                SELECT * FROM accounts WHERE Username = '{username}';
            ''')
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            else:
                cursor.execute(f'''
                               INSERT INTO accounts(username, password, email) 
                               VALUES ('{username}','{password}','{email}');
                           ''')
                mysql.connection.commit()
                msg = 'Account Successfully Created'
                cursor.close()

        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        return render_template('register.html', msg=msg)


@app.route('/home/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('Username', None)
    # Redirect to login page
    return render_template('logout.html')


@app.route('/query', methods=['GET', 'POST'])
def query():
    result = check_table('conversion')
    if result:
        default = {'Appid': '', 'mouza': '', 'khata': '', 'tarea': '', 'doa': '', 'olr': ''}
        if request.method == 'POST' and 'AppID' in request.form:
            appid = request.form['AppID']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f'''
                SELECT AppID,mouza,khata,tarea,doa,olr 
                FROM conversion
                WHERE AppID = {appid}
            ''')
            res = cursor.fetchone()
            print(res)
            if res:
                msg = "Data Found"
                return render_template('query.html', data=res, msg=msg)
            else:
                msg = " Data not found"
                return render_template('query.html', msg=msg)

        return render_template('query.html')


@app.route('/query/<int:AppID>')
def delete(AppID):
    print(AppID)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'''
                    DELETE FROM conversion 
                    WHERE AppID = {AppID}
                    ;''')
    mysql.connection.commit()
    cursor.close()
    msg = "Data Deleted"
    return render_template('query.html', msg=msg)


@app.route('/update/<int:AppID>', methods=['GET', 'POST'])
def update(AppID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'''
                        SELECT *
                        FROM conversion
                        WHERE AppID = {AppID}
                   ;''')
    result = cursor.fetchone()
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        contact = request.form['contact']
        mouza = request.form['mouza']
        khata = request.form['khata']
        plot = request.form['plot']
        tarea = request.form['tarea']
        doa = request.form['doa']
        payment1 = request.form['payment1']
        payment2 = request.form['payment2']
        tID = request.form['tID']
        olr = request.form['olr']

        cursor.execute(f'''
                UPDATE conversion
                SET firstName = '{firstname}',lastName = '{lastname}',contact= {contact},mouza='{mouza}',
                khata = '{khata}', plot = '{plot}', tarea = {tarea}, payment1 = {payment1}, payment2 = {payment2},
                tID = '{tID}', olr = '{olr}', doa = DATE '{doa}'
                WHERE AppID = {AppID}
            ;''')
        mysql.connection.commit()
        cursor.close()
        msg = "Update Successful"
        return redirect(url_for('query'))

    return render_template('update.html', data=result)


@app.route("/insert", methods=['GET', 'POST'])
def insert():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    check = check_table('conversion')
    if check:
        if request.method == 'POST':
            AppID = request.form['AppID']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            contact = request.form['contact']
            mouza = request.form['mouza']
            khata = request.form['khata']
            plot = request.form['plot']
            tarea = request.form['tarea']
            payment1 = request.form['payment1']
            payment2 = request.form['payment2']
            tID = request.form['tID']
            olr = request.form['olr']
            doa = request.form['doa']

            cursor.execute(f'''
                    INSERT INTO conversion
                     VALUES ({AppID},'{firstname}','{lastname}',{contact},'{mouza}','{khata}','{plot}',{tarea},{payment1},
                     {payment2},'{tID}','{olr}',DATE '{doa}')
                ;''')
            mysql.connection.commit()
            cursor.close()
            msg = "Insert Successful"
            return render_template('add.html', msg=msg)
    return render_template('add.html')


@app.route('/review', methods=['GET', 'POST'])
def review():
    check = check_table('review')
    if check:
        LoginID = session['id']
        Username = session['Username']
        if request.method == 'POST':
            name = request.form['name']
            contact = request.form['contact']
            email = request.form['email']
            comment = request.form['comment']
            rating = request.form['rating']
            currentdate = datetime.utcnow().strftime('%Y-%m-%d')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f'''
                INSERT INTO review(LOGINID, USERNAME, NAME, CONTACT, EMAIL, COMMENT, RATING, CURRENTDATE)
                VALUES ({LoginID},'{Username}','{name}',{contact},'{email}','{comment}',{rating},DATE '{currentdate}');
            ''')
            mysql.connection.commit()
            cursor.close()

    return render_template('reviews.html', username=Username)


if __name__ == '__main__':
    app.run(debug=True)
