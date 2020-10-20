from datetime import timedelta
from flask import Flask, render_template, url_for, request, flash, session
from flask_mysqldb import MySQL
from werkzeug.utils import redirect
import datetime
from flask import request
import socket
import re
from binascii import hexlify
app = Flask(__name__)
app.static_folder = 'static'
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.secret_key = ""
mysql = MySQL(app)
app.permanent_session_lifetime = timedelta(minutes=60)
@app.route('/')
def entry():
    return redirect(url_for('login'))

@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["email"]
        password = request.form["password"]
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM creds WHERE username = %s AND password = %s', (username, password,)) #Get Password From MySQL Database
        results = cur.fetchall() #Sets results to value
        if results: #If value is retured from MYSQL Database...
            session["username"] = username
            iprecieve = mysql.connection.cursor()
            iprecieve.execute('SELECT IPS FROM IPS WHERE username = %s', (username,))
            ipreturn = iprecieve.fetchone()
            ipreturn = str(ipreturn)
            ipreturn = ipreturn.replace("(", "").replace(")", "").replace(",", "").replace("b", "").replace("'", "")
            print(ipreturn)
            if ipreturn != "None": #If there is an ip in the database
                ipadress = request.remote_addr #Get IP of Computer
                if ipreturn == ipadress: #If IPS Match
                     pass
                else:
                    print("YES")
                    session.pop("username", None)
                    return redirect(url_for("login"))
            else:
                ipadress = request.remote_addr
                ipinsert = mysql.connection.cursor()
                ipinsert.execute("INSERT INTO IPS (IPS, username) VALUES (%s, %s)", (ipadress, username,))
                mysql.connection.commit()
                session.pop("username", None)
                return redirect(url_for("login"))
            return redirect(url_for("home"))
        else:
            flash('Incorrect username or password. Please try again!')
            return redirect(url_for("login"))
    else:
        if "username" in session:
            return redirect(url_for("home"))
        else:
            return render_template("login.html")

@app.route("/home", methods = ["GET", "POST"])
def home():
    if "username" in session:
        username = session["username"]
        if request.form.get('logout_button') == 'Log Out':
            session.pop("username", None)
            return redirect(url_for("login"))
        return render_template('index.html', username=username)
    else:
        return redirect(url_for("login"))


@app.route("/tickets", methods=["GET", "POST"])
def tickets():
    global dropdownCheck1, dropdownCheck2, dropdownCheck3, finalstatus, showstatus1, showstatus2, showstatus3
    if "username" in session:
        username = session["username"]
        curs = mysql.connection.cursor()
        curs.execute('SELECT showstatus FROM creds WHERE username = %s', (username,))
        showstatus = curs.fetchone()
        showstatus = str(showstatus)
        showstatus = showstatus.replace("(", "").replace(")", "").replace(",", "")
        showstatusdic = {"123":"1,2,3", "1": "1", "12": "1,2", "13": "1,3", "23": "2,3", "2": "2", "3": "3"}
        finalshowstatus = showstatusdic[showstatus]
        finalshowstatuslen = len(finalshowstatus)
        finalshowstatussplit = finalshowstatus.split(",", finalshowstatuslen)
        showstatus1 = 0
        showstatus2 = 0
        showstatus3 = 0
        if len(finalshowstatussplit) == 1:
            showstatus1 = finalshowstatussplit[0]
        if len(finalshowstatussplit) == 2:
            showstatus1 = finalshowstatussplit[0]
            showstatus2 = finalshowstatussplit[1]
        if len(finalshowstatussplit) == 3:
            showstatus1 = finalshowstatussplit[0]
            showstatus2 = finalshowstatussplit[1]
            showstatus3 = finalshowstatussplit[2]
        cur = mysql.connection.cursor()
        cur.execute('SELECT idticket_id,problem,OS,Browser,Time,Contact,Status,Technitian, Communication FROM ticket_id WHERE status = %s OR status = %s OR status = %s ORDER BY idticket_id DESC', (showstatus1, showstatus2, showstatus3))
        if request.form.get('submit_button') == 'Submit1' or request.form.get('submit_button') == 'Submit2' or request.form.get('submit_button') == 'Submit3':
            selection1 = request.form.getlist('Status1')
            selection2 = request.form.getlist('Status2')
            selection3 = request.form.getlist('Status3')
            if selection1:
                selection_changed1, ids1 = selection1[0].split()
                cur = mysql.connection.cursor()
                cur.execute("UPDATE ticket_id SET Status = %s WHERE idticket_id = %s", (selection_changed1, ids1))
                cur.execute("UPDATE ticket_id SET Technitian = %s WHERE idticket_id = %s", (username, ids1))
                mysql.connection.commit()
            elif selection2:
                selection_changed2, ids2 = selection2[0].split()
                cur = mysql.connection.cursor()
                cur.execute("UPDATE ticket_id SET Status = %s WHERE idticket_id = %s", (selection_changed2, ids2))
                cur.execute("UPDATE ticket_id SET Technitian = %s WHERE idticket_id = %s", (username, ids2))
                mysql.connection.commit()
            elif selection3:
                selection_changed3, ids3 = selection3[0].split()
                cur = mysql.connection.cursor()
                cur.execute("UPDATE ticket_id SET Status = %s WHERE idticket_id = %s", (selection_changed3, ids3))
                cur.execute("UPDATE ticket_id SET Technitian = %s WHERE idticket_id = %s", (username, ids3))
                mysql.connection.commit()
            return redirect(url_for("tickets"))
        elif request.form.get('SaveStatus_button') == 'SaveStatus':
            global dropdownCheck1, dropdownCheck2, dropdownCheck3
            dropdownCheck1 = request.form.get('dropdownCheck1')
            dropdownCheck2 = request.form.get('dropdownCheck2')
            dropdownCheck3 = request.form.get('dropdownCheck3')
            finalstatus = 0
            updatestat1 = 0
            updatestat2 = 0
            updatestat3 = 0
            finalstatusdic = {"123": "1,2,3", "1": "1", "12": "1,2", "13": "1,3", "23": "2,3", "2": "2", "3": "3"}
            if dropdownCheck1:
                updatestat1 = 1
            if dropdownCheck2:
                updatestat2 = 2
            if dropdownCheck3:
                updatestat3 = 3
            def concat(a, b, c):
                return int(f"{a}{b}{c}")
            finalstatusupdate = concat(updatestat1, updatestat2, updatestat3)
            finalstatusupdate = str(finalstatusupdate)
            finalstatusupdate = finalstatusupdate.strip('0')
            finalstatusupdate = int(finalstatusupdate)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE creds SET showstatus = %s WHERE username = %s", (finalstatusupdate, username))
            mysql.connection.commit()
            return redirect(url_for("tickets"))
        elif request.form.get('logout_button') == 'Log Out':
            session.pop("username", None)
            return redirect(url_for("login"))
        return render_template('tickets.html', items = cur.fetchall())
    else:
        return redirect(url_for("login"))

@app.route("/submitticket", methods=["GET", "POST"])
def submitticket():
    if "username" in session:
        username = session["username"]
        if request.form.get('logout_button') == 'Log Out':
            session.pop("username", None)
            return redirect(url_for("login"))
        elif request.method == "POST":
            Browser_ = request.form['Browser']
            Operating_System = request.form['Operating_system']
            email = username
            Problem = request.form['Problem']
            ids = None
            Technitian = "None"
            status = 1 #Default for Not started
            Communication = "Assigned Tickets"
            currenttime = datetime.datetime.now()
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO ticket_id (idticket_id, problem, OS, Browser, Time, Contact, Status, Technitian, Communication) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ids,Problem,Operating_System,Browser_,currenttime,email,status,Technitian, Communication))
            mysql.connection.commit()
        return render_template('submitticket.html', username=username)
    else:
        if request.form.get('login_button') == 'Login':
            return redirect(url_for("login"))
        elif request.method == "POST":
            Browser_ = request.form['Browser']
            Operating_System = request.form['Operating_system']
            email = request.form['email']
            Problem = request.form['Problem']
            ids = None
            Technitian = "None"
            Communication = "Email"
            status = 1  # Default for Not started
            currenttime = datetime.datetime.now()
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO ticket_id (idticket_id, problem, OS, Browser, Time, Contact, Status, Technitian, Communication) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ids,Problem,Operating_System,Browser_,currenttime,email,status,Technitian, Communication))
            mysql.connection.commit()
        return render_template('submitticketlogin.html')
@app.route('/assignedtickets/', methods=["GET", "POST"])
def assignedtickets():
    if "username" in session:
        username = session["username"]
        cur = mysql.connection.cursor()
        cur.execute('SELECT idticket_id,problem,OS,Browser,Time,Contact FROM ticket_id WHERE Status = "2" AND Technitian = %s ORDER BY idticket_id DESC', (username,))
        if request.form.get('submit_button_current_tickets') == 'Resolve':
            ticket_id = request.form.get('ticket_id') #FIXED BUG BY PUTTING FORM IN FOR LOOP
            session["ticket_id"] = ticket_id
            return redirect(url_for("resolveticket"))
        if request.form.get('logout_button') == 'Log Out':
            session.pop("username", None)
            return redirect(url_for("login"))
        return render_template('assignedtickets.html', items=cur.fetchall())
    else:
        return redirect(url_for("login"))
@app.route('/resolveticket/', methods=["GET", "POST"])
def resolveticket():
    if "username" in session:
        username = session["username"]
        ticket_id_passed = session.get("ticket_id", None)
        ticket_id_passed = str(ticket_id_passed)
        str_required = "t"
        finalstring = "".join((ticket_id_passed, str_required))
        finalstring = str(finalstring)
        cur = mysql.connection.cursor()
        cur.execute('SELECT idticket_id,problem,OS,Browser,Time,Contact,Communication FROM ticket_id WHERE idticket_id = %s', (ticket_id_passed,))
        curs = mysql.connection.cursor()
        curs.execute("SHOW TABLES LIKE %s", [finalstring])
        result = curs.fetchone()
        commentnumber = None
        if result:
            curs2 = mysql.connection.cursor()
            curs2.execute('SELECT * FROM ' + finalstring)
        else:
            curs2 = mysql.connection.cursor()
            curs2.execute("CREATE TABLE " + finalstring + " (commentnumber INT NOT NULL AUTO_INCREMENT, username VARCHAR(255) NOT NULL, comment VARCHAR(255) NOT NULL, PRIMARY KEY (commentnumber))")
            mysql.connection.commit()
        if request.form.get('comment_button') == 'comment_button':
            WriteComment = request.form['WriteComment']
            WriteComment = str(WriteComment)
            curs4 = mysql.connection.cursor()
            curs4.execute("INSERT INTO " + finalstring + " (commentnumber,username, comment) VALUES (%s, %s, %s)",
                          (commentnumber, username, WriteComment))
            mysql.connection.commit()
            return redirect(url_for('resolveticket'))
        return render_template('resolveticket.html', ticket_id_passed=ticket_id_passed, items=cur.fetchall(),comments = curs2.fetchall())
    else:
        return redirect(url_for("login"))
@app.route('/yourtickets/', methods=["GET", "POST"])
def yourtickets():
    if "username" in session:
        username = session["username"]
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT idticket_id,problem,OS,Browser,Time,Contact FROM ticket_id WHERE Contact = %s ORDER BY idticket_id DESC',
            (username,))
        if request.form.get('submit_button_current_tickets') == 'Resolve':
            your_ticket_id = request.form.get('your_ticket_id')  # FIXED BUG BY PUTTING FORM IN FOR LOOP
            session["your_ticket_id"] = your_ticket_id
            return redirect(url_for("resolveyourtickets"))
        if request.form.get('logout_button') == 'Log Out':
            session.pop("username", None)
            return redirect(url_for("login"))
        return render_template('yourtickets.html', items=cur.fetchall())
    else:
        return redirect(url_for("login"))
@app.route('/resolveyourtickets/', methods=["GET", "POST"])
def resolveyourtickets():
    if "username" in session:
        username = session["username"]
        your_ticket_id = session["your_ticket_id"]
        your_ticket_id = str(your_ticket_id)
        str_required = "t"
        yourfinalstring = "".join((your_ticket_id, str_required))
        yourfinalstring = str(yourfinalstring)
        cur = mysql.connection.cursor()
        cur.execute('SELECT idticket_id,problem,OS,Browser,Time,Contact,Communication FROM ticket_id WHERE idticket_id = %s', (your_ticket_id,))
        curs = mysql.connection.cursor()
        curs.execute("SHOW TABLES LIKE %s", [yourfinalstring])
        result = curs.fetchone()
        commentnumber = None
        if result:
            curs2 = mysql.connection.cursor()
            curs2.execute('SELECT * FROM ' + yourfinalstring)
        else:
            curs2 = mysql.connection.cursor()
            curs2.execute("CREATE TABLE " + yourfinalstring + " (commentnumber INT NOT NULL AUTO_INCREMENT, username VARCHAR(255) NOT NULL, comment VARCHAR(255) NOT NULL, PRIMARY KEY (commentnumber))")
            mysql.connection.commit()
        if request.form.get('logout_button') == 'Log Out':
            session.pop("username", None)
            return redirect(url_for("login"))
        if request.form.get('comment_button') == 'comment_button':
            WriteComment = request.form['WriteComment']
            WriteComment = str(WriteComment)
            curs4 = mysql.connection.cursor()
            curs4.execute("INSERT INTO " + yourfinalstring + " (commentnumber,username, comment) VALUES (%s, %s, %s)",
                          (commentnumber, username, WriteComment))
            mysql.connection.commit()
            return redirect(url_for('resolveyourtickets'))
        return render_template('resolveyourtickets.html', ticket_id_passed=your_ticket_id, items=cur.fetchall(),comments = curs2.fetchall())
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)