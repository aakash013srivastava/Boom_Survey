from flask import Flask,render_template,redirect,request,url_for,session,flash
from flask_mysqldb import MySQL,MySQLdb
import smtplib
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'BOOM_SURVEY'

mysql = MySQL(app)

app.secret_key= 'mysecretkey'


@app.route('/',methods=['GET'])
def home():
    if 'login' in session:
        return render_template('home.html',email = session['email'])
    return render_template('home.html',email = None)


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
    
        email = request.form['Email1']
        password = request.form['Password1']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM USERS WHERE email = % s AND password = % s', (email, password ))
        account = cursor.fetchone()
    
        if not account:
            try:
                cursor.execute(
                'INSERT INTO USERS(email,password) VALUES(%s,%s)', (email, password))
                mysql.connection.commit()
            except:
                print("Error while creating new user")
            else:
                cursor.close()
            return redirect(url_for('login',email=None))
        else:
            cursor.close()
            flash("Already Registered!Please Login")
            return (render_template('login.html',email=None,login=None))
    # Get request
    return render_template('register.html')

@app.route('/about',methods=['GET'])
def about():
    if session['login']:
        return render_template('about.html',login=session['login'],email=session['email'])
    return render_template('about.html',login=None,email=None)


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['Email1']
        password = request.form['Password1']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(
                'SELECT * FROM USERS WHERE email = % s AND password = % s', (email, password ))
            account = cursor.fetchone()
        except:
            print('Error while loggin in')
        else:
            if account:
                session['login']= True
                session['email'] = account['email']
                return redirect(url_for('home',email=account['email'],login = session['login']))
            else:
                return (render_template('login.html',email=None,login = None,message='Login again with right credentials'))

    if 'message' in request.args:
        return render_template('login.html',message=request.args['message'])
    return render_template('login.html',message=None)

@app.route('/logout')
def logout():
    session.pop('login',None)
    session.pop('email',None)
    return redirect(url_for('home'))


@app.route('/survey',methods=['GET','POST'])
def survey():
    email = session['email']
    print(email)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT * FROM SURVEY WHERE email = % s', (email,))
    account = cursor.fetchone()
    
    if request.method == "POST":
        
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        city_type = request.form['city-type']
        print(name,age,gender,city_type)
        try:
            cursor.execute(
            'INSERT INTO SURVEY(email,name,gender,age,city_type) VALUES(%s,%s,%s,%s,%s)', (email,name,gender,age,city_type))
            mysql.connection.commit()
        except Exception as e:
            print("Error while creating new survey\n",e)
        else:
            cursor.close()
        # send mail regarding survey completion


        message = "<b>This is SURVEY completion message.</b>"+"\n Name:"+name+"\n Gender:"+gender+"\n Age:"+age+"\n City_type:"+city_type

        sender = 'xyz@xyz@gmail.com'
        receiver = 'abc@abc.com'
        try:
            smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
            smtpObj.sendmail(sender, receiver, message)         
            print ("Successfully sent email")
        except smtplib.SMTPException:
            print ("Error: unable to send email")

        return redirect('/')
    
    # GET request
    else:
        
        return render_template('survey.html',login=session['login'],email=session['email'],submitted=account)
        

if __name__ == "__main__":
    app.run(debug=True)