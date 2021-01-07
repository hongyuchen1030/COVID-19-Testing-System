import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from pymysql.cursors import DictCursorMixin, Cursor
#import math to use eval() to transform a str to dictionary
from math import *
#this function is used in screen 7 cause python need the datetime to transform time and date
import datetime

#when cannot instal flask_mysqldb:
#export PATH=$PATH:/usr/local/mysql/bin
#pip3 install flask-mysqldb



# -------------------------- App Config (reference:https://github.com/miguelgrinberg/flasky/tree/master/app)-------------------------

app = Flask(__name__)
app.secret_key = 'team 84 is the best team'
#some configuration for Jinja templates
Flask.jinja_options = {'extensions': ['jinja2.ext.autoescape', 'jinja2.ext.with_'], 'line_statement_prefix': '%'}

app.config['MYSQL_HOST'] = 'localhost'

# User's configs, comment these back out
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'chy190354890'

app.config['MYSQL_DB'] = 'covidtest_fall2020'
# This code assumes you've already instantiated the DB

mysql = MySQL(app)


# -------------------------- Help Functions -------------------------
#this function is just for test
def transform_label(labels):
    list = []
    for i in range(len(labels)):
        list.append(labels[i][0])
    return list



# -------------------------- Platform Functions -------------------------
@app.route('/dashboard')
def dashboard():
    #First checks to see if there's someone logged in
    if 'user' in session:
        #Depending on their permissions, they get a different screen
        if session['userPerms'] == 'Admin':
            return render_template('adminDashboard.html')
        elif session['userPerms'] == 'Student':
            #Not sure if this should be homeScreenStudent, left this here as a default
            return render_template('studentDashboard.html')
        elif session['userPerms'] == 'Tester':
            return render_template('testerDashboard.html')
        elif session['userPerms'] == 'LabTech':
            return render_template('labTechDashboard.html')
        elif session['userPerms'] == 'LabTech+Tester':
            return render_template('labTechTesterDashboard.html')
        return "Invalid user permissions, try logging out and back in"
    #If not logged in, pushes the user to the index page
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    #All this does is clear the session information, meaning that the app no longer knows user or user-perms
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

#Screen 1: Login
#This is poorly named, but this is the login form
@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/regform')
def registForm():
    return render_template('regform.html')


#a very basic screen collection for test
@app.route('/EachScreen')
def eachScreen():
    return render_template('EachScreen.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return redirect(url_for('form'))

    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        username = request.form['Username']
        password = request.form['Password']
        select_statement = "SELECT * FROM USER WHERE username = %s AND MD5(%s) = user_password"
        result = cursor.execute(select_statement, (username, password))
        #If it finds the user credentials in the DB, it then seeks to update the session accordingly
        if result:
            session['user'] = username
            checkForPermissions()
            cursor.close()
            return redirect(url_for('dashboard'))
        cursor.close()
        return "Login Failed"

#Screen 1 to Home Screen decided by user's role
def checkForPermissions():
    #These SQL statements check to see which class of user is logged in, and updates the session information accordingly
    cursor = mysql.connection.cursor()
    select_statement = "SELECT * FROM ADMINISTRATOR WHERE admin_username = %s"
    result = cursor.execute(select_statement, (session['user']))
    if result:
        session['userPerms'] = 'Admin'
        cursor.close()
        return
    select_statement = "SELECT * FROM STUDENT WHERE student_username = %s"
    result = cursor.execute(select_statement, (session['user']))
    if result:
        session['userPerms'] = 'Student'
        cursor.close()
        return
    select_statement = "SELECT * FROM LABTECH WHERE labtech_username = %s"
    result = cursor.execute(select_statement, (session['user']))
    if result:
        session['userPerms'] = 'LabTech'
    select_statement = "SELECT * FROM SITETESTER WHERE sitetester_username = %s"
    result = cursor.execute(select_statement, (session['user']))
    if result and 'userPerms' in session and session['userPerms'] == 'LabTech':
        session['userPerms'] = 'LabTech+Tester'
        cursor.close()
        return
    elif result:
        session['userPerms'] = 'Tester'
        cursor.close()
        return
    cursor.close()
    return

#-------------------------------Registration Screen for Student----------------------
@app.route('/StudentRegister',methods=['GET','POST'])
def getStuRegistRequest():#Register as student
    if request.method == 'GET':
        hint = ""
        return render_template('StudentRegister.html',hint = hint)
    elif request.method == 'POST':
        cursor = mysql.connection.cursor()
        #SQL command
        userName = request.form.get('Username')

        #Validate the username and name
        #1 username must be unique
        sql = "select username from USER"
        try:
            cursor.execute(sql)
        except pymysql.IntegrityError or KeyError as e:
            return "unable to register"+str(e)
        else:
            mysql.connection.commit()
            content = cursor.fetchall()
            names = []
            for name in content:
                names.append(name[0])

            if userName in names:
                hint = "Sorry this username already exist"
                return render_template('StudentRegister.html', hint=hint)

        #Validate the username and name
        #2 combination of “First Name” and “Last Name” is unique for all users
        fName = request.form.get('FName')
        lName = request.form.get('LName')
        sql = "select username from USER where fname = %s and lname = %s"
        try:
            cursor.execute(sql,(fName,lName))
        except pymysql.IntegrityError or KeyError as e:
            return "unable to register"+str(e)
        else:
            mysql.connection.commit()
            content = cursor.fetchall()

            if len(content) != 0:
                hint = "Sorry your name is already in our database, please login"
                return render_template('StudentRegister.html', hint=hint)


        email = request.form.get('Email')

        passWord = request.form.get('Password')
        confirmPass = request.form.get('ConfirmPwd')

    #see if the password match
    if confirmPass != passWord:
        return "Sorry, your passwords don't match"

    #no need to change the password to hashcode here since it's done in the mysql procedure

    houseType = request.form.get('HouseType')
    location = request.form.get('Location')

    try:
        cursor.callproc("register_student",[userName,email,fName,lName,location,houseType,passWord])
    except pymysql.IntegrityError or KeyError as e:
        return "unable to register"+str(e)
    else:
        mysql.connection.commit()
        return redirect(url_for('login'))

#--------------------------Registration Screen for employee
@app.route('/EmployeeRegister', methods=['GET', 'POST'])
def getEmpRegistRequest():  # Register as employee
    if request.method == 'GET':
        hint = ""
        return render_template('EmployeeRegister.html',hint=hint)
    elif request.method == 'POST':
        cursor = mysql.connection.cursor()
        # SQL command

        userName = request.form.get('Username')
        #Validate the username and name
        #1 username must be unique
        sql = "select username from USER"
        try:
            cursor.execute(sql)
        except pymysql.IntegrityError or KeyError as e:
            return "unable to register"+str(e)
        else:
            mysql.connection.commit()
            content = cursor.fetchall()
            names = []
            for name in content:
                names.append(name[0])

            if userName in names:
                hint = "Sorry this username already exist"
                return render_template('EmployeeRegister.html', hint=hint)

        #Validate the username and name
        #2 combination of “First Name” and “Last Name” is unique for all users
        fName = request.form.get('FName')
        lName = request.form.get('LName')
        sql = "select username from USER where fname = %s and lname = %s"
        try:
            cursor.execute(sql,(fName,lName))
        except pymysql.IntegrityError or KeyError as e:
            return "unable to register"+str(e)
        else:
            mysql.connection.commit()
            content = cursor.fetchall()

            if len(content) != 0:
                hint = "Sorry your name is already in our database, please login"
                return render_template('EmployeeRegister.html', hint=hint)


        email = request.form.get('Email')
        passWord = request.form.get('Password')
        confirmPass = request.form.get('ConfirmPwd')
        # see if the password match
        if confirmPass != passWord:
            return "Sorry, your passwords don't match"

        employee = request.form.getlist('employType')
        phone = request.form.get('Phone')
        if len(employee) == 2:
            lab = True
            tester = True
            try:
                cursor.callproc("register_employee",[userName,email,fName,lName,phone,lab,tester,passWord])
            except pymysql.IntegrityError or KeyError as e:
                return "unable to register" + str(e)
            else:
                mysql.connection.commit()
                return redirect(url_for('login'))
        elif len(employee) == 1:
            job = employee[0]
            if job == "labTech":
                try:
                    cursor.callproc("register_employee",
                                    [userName, email, fName, lName, phone, True, False, passWord])
                except pymysql.IntegrityError or KeyError as e:
                    return "unable to register" + str(e)
                else:
                    mysql.connection.commit()
                    return redirect(url_for('login'))
            elif job == "siteTester":
                try:
                    cursor.callproc("register_employee",
                                    [userName, email, fName, lName, phone, False, True, passWord])
                except pymysql.IntegrityError or KeyError as e:
                    return "unable to register" + str(e)
                else:
                    mysql.connection.commit()
                    return redirect(url_for('login'))

# -------------------------- All Users Experience -----------------------
# Screen 4
# 1. only student can do it and he/she doesn't need to upload the form, the system should know who he/she is
# 2. there is no "all" selection
filter_data = {}
reverse = False
@app.route('/studentViewTestResults', methods=['GET', 'POST'])
def studentView():
    if session['userPerms'] != 'Student':
        return "you have no permission to this screen"
    global filter_data
    global reverse
    if request.method == 'GET':
        return render_template('studentViewTestResults.html')
    elif request.method == 'POST':
        labels = ['Test ID#', 'Timeslot Date', 'Date Processed', 'Pool Status', 'Status']
        if request.form.get('filter_column') is not None:
            counter = {}
            column = eval(request.form.get('filter_column'))-1
            stuff = eval(request.form.get('content_filter'))
            print("column:",type(column),"stuff:",type(stuff))
            reverse = True if reverse == False else False
            new_content = sorted(stuff,key=lambda x:"" if x[int(column)] is None else str(x[int(column)]),reverse=reverse)
            return render_template('studentViewTestResults.html', labels=labels, content=new_content,
                                   filter_data=filter_data)


        cursor = mysql.connection.cursor()

        # Will change the way of getting username after the front end is done

        userName = session['user']
        status = None if request.form.get('Status') == '' else request.form.get('Status')
        startDate = None if request.form.get('TimeStart') == '' else request.form.get('TimeStart')
        endDate = None if request.form.get('TimeEnd') == '' else request.form.get('TimeEnd')
        stat = "All" if status is None else status
        sd = "All" if startDate is None else startDate
        ed = "All" if endDate is None else endDate

        filter_data = {"Status":stat,"StartDate":sd,"EndDate":ed}
        try:
            result = cursor.callproc("student_view_results", [userName, status, startDate, endDate])
        except pymysql.IntegrityError or KeyError as e:
            return "unable to view because " + str(e)
        else:
            # print the view to the html

            # select from the student_view_results_result
            sql = "select * from student_view_results_result"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall()




            print(content)
            return render_template('studentViewTestResults.html', labels=labels, content=content,filter_data=filter_data)
        
#Screen 5: Explore test result
@app.route('/exploreTestResult', methods=['GET', 'POST'])
def exploreTestResult():
    if session['userPerms'] != 'Student':
        return "you have no permission to this screen"
    if request.method == 'GET':
        return render_template('exploreTestResult.html')
    elif request.method == 'POST':
        cursor = mysql.connection.cursor()
        testid = request.form.get('Testid')

        try:
            result = cursor.callproc("explore_results", [testid])
        except pymysql.IntegrityError or KeyError as e:
            return "unable to view because " + str(e)
        else:
            # print the view to the html

            # select from the student_view_results_result
            sql = "select * from explore_results_result"
            cursor.execute(sql)
            #one row code below may be not neccessary
            mysql.connection.commit()
            content = cursor.fetchall()

            # get the field name
            sql = "SHOW FIELDS FROM explore_results_result"
            cursor.execute(sql)
            labels = cursor.fetchall()
            mysql.connection.commit()
            labels = ['Test ID#','Date Tested', 'Timeslot', 'Testing Location', 'Date Processed', 'Pooled Result', 'Individual Result','Processed By']
            print(content)
            if content == ():
                return "This test has not been processed yet"
            # visualization template source:
            # https://blog.csdn.net/a19990412/article/details/84955802

            return render_template('exploreTestResult.html', labels=labels, content=content)

#Screen 6: Aggregate Results
housing_type = ''
site = ''
@app.route('/aggregateResult', methods=['GET', 'POST'])
def aggregateResult():
    global housing_type,site
    if request.method == 'GET':
        #get all housing_type
        cursor = mysql.connection.cursor()
        sql_house = "select distinct housing_type from student order by housing_type"
        cursor.execute(sql_house)
        housing_type = transform_label(cursor.fetchall())

        # get all site name
        sql_site = "select distinct site_name from site order by site_name"
        cursor.execute(sql_site)
        site = transform_label(cursor.fetchall())

        print("housing_type1: ",housing_type,"site1: ",site)

        return render_template('aggregateResult.html', housing_type = housing_type,site = site)

    elif request.method == 'POST':
        cursor = mysql.connection.cursor()

        Location = None if request.form.get('Location') == '' else request.form.get('Location')
        Housing = None if request.form.get('Housing') == '' else request.form.get('Housing')
        Testing_site = None if request.form.get('testingSite') == '' else request.form.get('testingSite')
        startDate = None if request.form.get('TimeStart') == '' else request.form.get('TimeStart')
        endDate = None if request.form.get('TimeEnd') == '' else request.form.get('TimeEnd')
        print("location: ",Location)
        ld = "ALL" if Location is None else Location
        hou = "ALL" if Housing is None else Housing
        ts = "ALL" if Testing_site is None else Testing_site
        sd = "ALL" if startDate is None else startDate
        ed = "ALL" if endDate is None else endDate

        filter_data = {"Location":ld,"Housing":hou,"Testing_site":ts,"StartDate":sd,"EndDate":ed}
        try:
            cursor.callproc("aggregate_results", [Location,Housing,Testing_site,startDate,endDate])
        except pymysql.IntegrityError or KeyError as e:
            return "unable to view because " + str(e)
        else:
            # print the view to the html

            # select from the student_view_results_result
            sql = "select * from aggregate_results_result"
            cursor.execute(sql)
            #one row code below may be not neccessary
            mysql.connection.commit()
            content = cursor.fetchall()

            # get the field name
            # sql = "SHOW FIELDS FROM aggregate_results_result"
            # cursor.execute(sql)
            # labels = cursor.fetchall()
            # mysql.connection.commit()
            total = 0
            for i in range(len(content)):
                total += content[i][1]

            labels = ['Total',str(total),'100%']
            print("content: ", content)
            print("housing_type: ",housing_type,"site:",site)
            return render_template('aggregateResult.html', labels=labels, content=content, housing_type = housing_type,site = site,filter_data=filter_data)

# now we need to manually add a username here for test:
# Screen 7a:
testsite = ''
filter_data = {}
@app.route('/testSignUpFilter', methods=['GET', 'POST'])
def testSignUpFilter():
    if session['userPerms'] != 'Student':
        return "you have no permission to this screen"
    global testsite
    global filter_data
    username = session['user']
    if request.method == 'GET':
        sql_site = "SELECT site_name from site where location = (select location from student where student_username = '{username}')".format(username=username)
        cursor = mysql.connection.cursor()
        cursor.execute(sql_site)
        testsite = transform_label(cursor.fetchall())
        print("testsite1: ",testsite)
        return render_template('testSignUpFilter.html',testsite = testsite,username = username)
    elif request.method == 'POST':
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        #username = request.form.get('Username')
        #just for test: give username a specific name
        Testing_site = None if request.form.get('testingSite') == '' else request.form.get('testingSite')
        startDate = None if request.form.get('DateStart') == '' else request.form.get('DateStart')
        endDate = None if request.form.get('DateEnd') == '' else request.form.get('DateEnd')
        startTime = None if request.form.get('startTime') == '' else request.form.get('startTime')
        endTime = None if request.form.get('endTime') == '' else request.form.get('endTime')
        ts = "All" if Testing_site is None else Testing_site
        sd = "All" if startDate is None else startDate
        ed = "All" if endDate is None else endDate
        st = "All" if startTime is None else startTime
        et = "All" if endTime is None else endTime
        filter_data = {"Testing Site":ts,"StartDate":sd,"EndDate":ed,"Start Time":st,"End Time":et}



        print("data:",[username,Testing_site,startDate,endDate,startTime,endTime])
        try:
            result = cursor.callproc("test_sign_up_filter", [username,Testing_site,startDate,endDate,startTime,endTime])
        except pymysql.IntegrityError or KeyError as e:
            return "unable to view because " + str(e)
        else:
            # print the view to the html
            # select from the student_view_results_result
            sql = "select appt_date, appt_time, street, site_name from test_sign_up_filter_result order by appt_date,appt_time"
            cursor.execute(sql)
            #one row code below may be not neccessary
            mysql.connection.commit()
            content = cursor.fetchall()

            mysql.connection.commit()
            labels = ['Date','Time','Site Address','Test Site','Sign Up']
            print("content:",content)
            # visualization template source:
            # https://blog.csdn.net/a19990412/article/details/84955802
            print("testsite2: ",testsite)
            return render_template('testSignUpFilter.html', labels=labels, content=content,filter_data = filter_data, user=username,testsite=testsite,username=username)

#Screen 7b:
@app.route('/testSignUp', methods=['GET', 'POST'])
def testSignUp():
    if request.method == 'GET':
        return render_template('testSignUp.html')
    elif request.method == 'POST':
        username = session['user']
        #test whether there exists any pending tests
        sql_test = "SELECT * FROM "
        data = eval(request.form.get('data'))
        Testing_site = data['site_name']
        Date = data['appt_date']
        Time = data['appt_time']


        #get a new testid to register
        cursor = mysql.connection.cursor()
        sql1 = 'SELECT test_id FROM test order by test_id'
        cursor.execute(sql1)
        all_testid = cursor.fetchall()
        Testid = int(all_testid[-1][0])+1
        cursor.execute('SELECT count(*) from test')
        number = cursor.fetchone()
        print("number:",number)

        # username = request.form.get('Username')
        # Testid = request.form.get('Testid')
        # Testing_site = None if request.form.get('testingSite') == '' else request.form.get('testingSite')
        # Date = None if request.form.get('Date') == '' else request.form.get('Date')
        # Time = None if request.form.get('Time') == '' else request.form.get('Time')
        print([username,Testing_site,str(Date),str(Time),str(Testid)])
        try:
            cursor.callproc("test_sign_up", [username,Testing_site,str(Date),str(Time),str(Testid)])
        except pymysql.IntegrityError or KeyError as e:
            return "unable to sign up" + str(e)
        else:
            mysql.connection.commit()
            cursor.execute('SELECT count(*) from test')
            after_number = cursor.fetchone()
            print("number:", after_number)
            if int(after_number[0]) == int(number[0]) + 1:
                return "You have successfully Signed up the Test"
            else:
                return "something went wrong!"



#Screen 8a:
filter_data = {}
reverse = False
@app.route('/tests_processed', methods=['GET', 'POST'])
def tests_processed():
    if session['userPerms'] != "LabTech+Tester" and session['userPerms'] != "LabTech":
        return "you have no permission to this screen"
    global filter_data
    global reverse
    username = session['user']
    if request.method == 'GET':
        return render_template('tests_processed.html',user=username)
    elif request.method == 'POST':
        labels = ['Test ID#', 'Pool id', 'Date Tested', 'Date Processed', 'Result']
        if request.form.get('filter_column') is not None:
            column = eval(request.form.get('filter_column'))-1
            stuff = eval(request.form.get('content_filter'))
            print("column:",type(column),"stuff:",type(stuff))
            reverse = True if reverse == False else False
            new_content = sorted(stuff,key=lambda x:"" if x[int(column)] is None else str(x[int(column)]),reverse=reverse)
            return render_template('tests_processed.html', labels=labels, content=new_content,user=username,
                                   filter_data=filter_data)
        cursor = mysql.connection.cursor()
        # username = request.form.get('labtechUsername')

        testStatus = None if request.form.get('testStatus') == '' else request.form.get('testStatus')
        startDate = None if request.form.get('DateStart') == '' else request.form.get('DateStart')
        endDate = None if request.form.get('DateEnd') == '' else request.form.get('DateEnd')
        ts = "All" if testStatus is None else testStatus
        sd = "All" if startDate is None else startDate
        ed = "All" if endDate is None else endDate

        filter_data = {"Test Status":ts,"StartDate":sd,"EndDate":ed}

        print("test: ",[startDate,endDate,testStatus,username])
        try:
            cursor.callproc("tests_processed", [startDate,endDate,testStatus,username])
        except pymysql.IntegrityError or KeyError as e:
            return "unable to view because " + str(e)
        else:
            # print the view to the html

            # select from the student_view_results_result
            sql = "select * from tests_processed_result"
            cursor.execute(sql)
            #one row code below may be not neccessary
            mysql.connection.commit()
            content = cursor.fetchall()

            print(content)


            return render_template('tests_processed.html', labels=labels, content=content,user=username,filter_data=filter_data)


#Screen 9: Viewpools
def pending_filter(content):
    pending = []
    for data in content:
        if data[-1] == 'pending':
            pending.append(data[0])
    return pending

filter_data = {}
reverse = False
@app.route('/viewPools',methods=['GET','POST'])
def viewPools():
    if session['userPerms'] != "LabTech+Tester" and session['userPerms'] != "LabTech":
        return "you have no permission to this screen"
    global filter_data
    global reverse
    if request.method =='GET':
        return render_template('viewPools.html')
    elif request.method == 'POST':
        labels = ['Test ID#', 'Pool id', 'Date Tested', 'Date Processed', 'Result']
        if request.form.get('filter_column') is not None:
            column = eval(request.form.get('filter_column'))-1
            stuff = eval(request.form.get('content_filter'))
            pending = request.form.get('pending1')
            print("column:",type(column),"stuff:",type(stuff))
            reverse = True if reverse == False else False
            new_content = sorted(stuff,key=lambda x:"" if x[int(column)] is None else str(x[int(column)]),reverse=reverse)
            return render_template('viewPools.html', labels=labels, content=new_content,pending=pending,
                                   filter_data=filter_data)

        cursor = mysql.connection.cursor()
        startDate = None if request.form.get('DateStart') == '' else request.form.get('DateStart')
        endDate = None if request.form.get('DateEnd') == '' else request.form.get('DateEnd')
        status = None if request.form.get("Status") == '' else request.form.get("Status")
        labtech = None if request.form.get('LabTech') == '' else request.form.get('LabTech')

        sd = "All" if startDate is None else startDate
        ed = "All" if endDate is None else endDate
        st = "All" if status is None else status
        lb = "ALL" if labtech is None else labtech
        filter_data = {"Status":st,"StartDate":sd,"EndDate":ed,"LabTech Name":lb}
        print([startDate,endDate,labtech,status])
        try:
            cursor.callproc("view_pools",[startDate,endDate,status,labtech])
        except pymysql.IntegrityError or KeyError as e:
            return "unable to view because " + str(e)
        else:
            #print the view to the html

            # select from the student_view_results_result
            sql = "select * from view_pools_result order by pool_id"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall()

            # get the field name
            sql = "SHOW FIELDS FROM view_pools_result"
            cursor.execute(sql)
            mysql.connection.commit()
            labels = ['Pool ID','Test Ids','Date Processed','Processed By','Pool Status']
            pending = pending_filter(content)
            print("pending: ",pending)
            #visualization template source:
            #https://blog.csdn.net/a19990412/article/details/84955802
            # content = sorted(content,key = lambda x:int(x[0]))

            return render_template('viewPools.html', labels=labels, content = content,pending=pending,filter_data=filter_data)


#==================================
#Screen 10a & 10b:
#For the frontend to this application, would be ideal if it doesn't allow user to submit without selecting exactly 1 - 7 tests.
@app.route('/createPool',methods=['GET','POST'])
def createPool():
    cursor = mysql.connection.cursor()
    try:
        sql = "select test_id, appt_date from test where pool_id is NULL"
        cursor.execute(sql)
        content = cursor.fetchall()
        mysql.connection.commit()
        if request.method =='GET':
                labels = ['Test ID', 'Date Tested']
                cursor.close()
                return render_template('createPool.html', content = content, labels = labels)
        elif request.method == 'POST':
            poolID = request.form.get('poolID')
            sql = "select * from pool where pool_id = " + poolID
            cursor.execute(sql)
            content2 = cursor.fetchall()
            mysql.connection.commit()
            if content2:
                return "You cannot remake an existing Pool, choose a different Pool ID"
            else:
                pool_flag = False
                testCount = 0
                for i in range(0,len(content)+1):
                    test = request.form.get(str(i))
                    if test:
                        testCount += 1
                if testCount < 1 or testCount > 7:
                    return "You must select 1 - 7 tests per pool"
                for i in range(0,len(content)+1):
                    test = request.form.get(str(i))
                    if test and not pool_flag:
                        result = cursor.callproc("create_pool",[poolID, test])
                        mysql.connection.commit()
                        pool_flag = True
                    elif test:
                        result2 = cursor.callproc("assign_test_to_pool",[poolID, test])
                        mysql.connection.commit()
                return redirect(url_for('dashboard'))
    except pymysql.IntegrityError or KeyError as e:
        return "unable to view because " + str(e)
    else:
        return redirect(url_for('dashboard'))
#Screen 11a & 11b:
#I believe this will mainly be used in creating links, all you need to point to a given pool is to append it to the link
@app.route('/processPools/<id>',methods=['GET','POST'])
def processPools(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.callproc("tests_in_pool",[id])
        sql = "select test_id, date_tested from tests_in_pool_result"
        cursor.execute(sql)
        content = cursor.fetchall()
        mysql.connection.commit()
        if request.method =='GET':
            sql = "select max(appt_date) from test where pool_id =" + id
            cursor.execute(sql)
            content2 = cursor.fetchall()
            mysql.connection.commit()
            labels = ["Test ID","Date Tested"]
            return render_template('processPools.html', id = id, minDate = content2[0][0] + datetime.timedelta(days=1), content = content, labels = labels)
        elif request.method == 'POST':
            #Need to check back over to see which are valid
            poolStatus = request.form.get('poolStatus')
            processDate = None if request.form.get('dateProcessed') == '' else request.form.get('dateProcessed')

            if not processDate:
                return "You must specify a process date"

            positiveCount = 0
            for indivTest in content:
                testResult = request.form.get(indivTest[0])
                if testResult == "positive":
                    positiveCount += 1

            if poolStatus == "negative":
                if positiveCount > 0:
                    return "Test result cannot be positive in a negative pool"
            elif poolStatus == "positive":
                if positiveCount < 1:
                    return "Positive pool requires a minimum of one positive test"

            cursor.callproc("process_pool",[id, poolStatus, processDate, session['user']])
            mysql.connection.commit()
            for indivTest in content:
                testResult = request.form.get(indivTest[0])
                cursor.callproc("process_test",[indivTest[0], testResult])
                mysql.connection.commit()
            return redirect(url_for('dashboard'))
    except pymysql.IntegrityError or KeyError as e:
        return "unable to view because " + str(e)
    else:
        return redirect(url_for('dashboard'))

#==================================





# -------------------------- Student Specific Experience ----------------

# @app.route('/studentView',methods=['GET','POST'])
# def studentView():
#     if request.method == 'GET':
#         return render_template('studentView.html')
#     elif request.method == 'POST':
#         cursor = mysql.connection.cursor()
#
#         #Will change the way of getting username after the front end is done
#         userName = request.form.get('Username')
#         status = request.form.get('Status')
#         startDate = None if request.form.get('TimeStart')  == '' else request.form.get('TimeStart')
#         endDate = None if request.form.get('TimeEnd') == '' else request.form.get('TimeEnd')
#
#
#         try:
#             result = cursor.callproc("student_view_results",[userName, status, startDate,endDate])
#         except pymysql.IntegrityError or KeyError as e:
#             return "unable to view because " + str(e)
#         else:
#             #print the view to the html
#
#             # select from the student_view_results_result
#             sql = "select * from student_view_results_result"
#             cursor.execute(sql)
#             mysql.connection.commit()
#             content = cursor.fetchall()
#
#             # get the field name
#             sql = "SHOW FIELDS FROM student_view_results_result"
#             cursor.execute(sql)
#             labels = cursor.fetchall()
#             mysql.connection.commit()
#             labels = ['Test ID#','Timeslot Date','Date Processed','Pool Status','Status']
#

#
#             return render_template('studentView.html', labels=labels, content=content)

# -------------------------- Tester Experience --------------------------

# -------------------------- LabTech Experience -------------------------

# -------------------------- Admin User Experience ----------------------

#Screen 14 in Description: Reassign Tester
#Screen 17 in Description: Self-Assign Tester
@app.route('/reassigntester',methods=['GET','POST'])
def reassigntester():
    if 'user' in session and session['userPerms'] == 'Admin':
        return redirect(url_for('viewTester'))
    elif 'user' in session and (session['userPerms'] == 'Tester' or session['userPerms'] == 'LabTech+Tester'):
        cursor = mysql.connection.cursor()
        try:
            result = cursor.callproc("tester_assigned_sites",[session['user']])
        except pymysql.IntegrityError or KeyError as e:
                return "unable to view because " + str(e)
        else:
            sql = "select * from tester_assigned_sites_result"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall()
            if request.method == 'POST':
                addSite = request.form.get('siteNameAdd')
                if(addSite != "None"):
                    try:
                        print(addSite)
                        result2 = cursor.callproc("assign_tester",[session['user'], addSite])
                    except pymysql.IntegrityError or KeyError as e:
                        return "Failed to Add"
                for entry in content:
                    if not request.form.get(entry[0]) or request.form.get(entry[0]) != 'assigned':
                        try:
                           result2 = cursor.callproc("unassign_tester",[session['user'], entry[0]])
                        except:
                            return "Failed to Remove"
            result = cursor.callproc("tester_assigned_sites",[session['user']])
            sql = "select * from tester_assigned_sites_result"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall()
            labels = ["Current Sites for user: " + session['user']]
            result = cursor.callproc("view_testers",[])
            sql = 'select name from view_testers_result where username ="' + session['user'] + '"'
            print(sql)
            cursor.execute(sql)
            mysql.connection.commit()
            fullName = cursor.fetchall()[0][0]
            sql = "select site_name from site where site_name not in (select * from tester_assigned_sites_result)"
            cursor.execute(sql)
            mysql.connection.commit()
            content2 = cursor.fetchall()
            realcontent = []
            for i in content2:
                realcontent.append(i[0])
            cursor.close()
            return render_template('testerSelfReassign.html', labels=labels, content=content, unassigned=realcontent, fullName = fullName)
    else:
        redirect(url_for('dashboard'))


#Screen 12a: Create an appointment
@app.route('/createAppointment',methods=['GET','POST'])
def createAppointment():
    if request.method == 'GET':
        if 'user' in session and session['userPerms'] == 'Admin':
            cursor = mysql.connection.cursor()
            sql = "select site_name from SITE"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall();
            allSites = []
            for site in content:
                allSites.append(site[0])

            cursor.close()
            hint = "You don't have last Operation"
            return render_template('createAppointment.html', allSites=allSites, hint=hint)
        elif 'user' in session and (session['userPerms'] == 'Tester' or session['userPerms'] == 'LabTech+Tester') :
            cursor = mysql.connection.cursor()
            userName = session['user']
            sql = "select site from WORKING_AT where username = %s"
            cursor.execute(sql,(userName))
            mysql.connection.commit()
            content = cursor.fetchall();
            allSites = []
            for site in content:
                allSites.append(site[0])

            cursor.close()
            hint = "You don't have last Operation"
            return render_template('createAppointment.html', allSites=allSites, hint=hint)



        else:
            return "Sorry you don't have the access to this screen"


    elif request.method == 'POST':
        if 'user' in session and session['userPerms'] == 'Admin':
            # Some visulization stuff:
            cursor = mysql.connection.cursor()
            sql = "select site_name from SITE"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall();
            allSites = []
            for site in content:
                allSites.append(site[0])

            #Now the real code
            cursor = mysql.connection.cursor()
            siteName = request.form.get('siteName')
            date = request.form.get('date')
            time = request.form.get('time')
            #See if duplicate appointments
            try:
                select_statement = "select * from Appointment where site_name = %s and appt_date = %s and appt_time = %s"
                result = cursor.execute(select_statement, (siteName, date,time))
            except pymysql.IntegrityError or KeyError as e:
                return "unable to create appointment beacuse "+str(e)
            else:
                mysql.connection.commit()
                content = cursor.fetchall();



                if len(content) != 0:
                    hint = "Sorry, appointment already exsit"

                    return render_template('createAppointment.html', allSites=allSites, hint = hint)

            #See if Overload Appointment for this site
            try:
                set = "select 10* count(distinct sitetester_username) from SITETESTER join WORKING_AT on sitetester_username = WORKING_AT.username where WORKING_AT.site = %s;"
                result = cursor.execute(set, (siteName))
            except pymysql.IntegrityError or KeyError as e:
                return "unable to create appointment beacuse "+str(e)
            else:
                mysql.connection.commit()
                maxNum = cursor.fetchall();
                maxNum = maxNum[0]
                try:
                    select_statement = "select count(*) from Appointment where site_name = %s and %s = appt_date"
                    result = cursor.execute(select_statement, (siteName, date))
                except pymysql.IntegrityError or KeyError as e:
                    return "unable to create appointment beacuse "+str(e)
                else:
                    mysql.connection.commit()
                    curNum = cursor.fetchall();
                    curNum = curNum[0]
                    if curNum >= maxNum:
                        hint = "Test site is overloaded, Please select another testsite "
                        return render_template('createAppointment.html', allSites=allSites, hint=hint)

            #If things are alright


            try:
                cursor.callproc("create_appointment",[siteName,date,time])
            except pymysql.IntegrityError or KeyError as e:
                return "unable to create appointment beacuse "+str(e)
            else:

                #Commit to the procedure call
                mysql.connection.commit()
                return render_template('createAppointment.html', allSites=allSites, hint ="You have successfully create an Appointment")
        elif 'user' in session and (session['userPerms'] == 'Tester' or session['userPerms'] == 'LabTech+Tester'):
            cursor = mysql.connection.cursor()
            userName = session['user']
            sql = "select site from WORKING_AT where username = %s"
            cursor.execute(sql,(userName))
            mysql.connection.commit()
            content = cursor.fetchall();
            allSites = []
            for site in content:
                allSites.append(site[0])

            cursor.close()
            hint = "You don't have last Operation"
            #Now the real code
            cursor = mysql.connection.cursor()
            siteName = request.form.get('siteName')
            date = request.form.get('date')
            time = request.form.get('time')
            #See if duplicate appointments
            try:
                select_statement = "select * from Appointment where site_name = %s and appt_date = %s and appt_time = %s"
                result = cursor.execute(select_statement, (siteName, date,time))
            except pymysql.IntegrityError or KeyError as e:
                return "unable to create appointment because "+str(e)
            else:
                mysql.connection.commit()
                content = cursor.fetchall();

                if len(content) != 0:
                    hint = "Sorry, appointment already exsit"

                    return render_template('createAppointment.html', allSites=allSites, hint = hint)

            #See if Overload Appointment for this site
            try:
                set = "select 10* count(distinct sitetester_username) from SITETESTER join WORKING_AT on sitetester_username = WORKING_AT.username where WORKING_AT.site = %s;"
                result = cursor.execute(set, (siteName))
            except pymysql.IntegrityError or KeyError as e:
                return "unable to create appointment beacuse "+str(e)
            else:
                mysql.connection.commit()
                maxNum = cursor.fetchall();
                maxNum = maxNum[0]
                try:
                    select_statement = "select count(*) from Appointment where site_name = %s and %s = appt_date"
                    result = cursor.execute(select_statement, (siteName, date))
                except pymysql.IntegrityError or KeyError as e:
                    return "unable to create appointment beacuse "+str(e)
                else:
                    mysql.connection.commit()
                    curNum = cursor.fetchall();
                    curNum = curNum[0]
                    if curNum >= maxNum:
                        hint = "Test site is overloaded Thank you for your hardwork "
                        return render_template('createAppointment.html', allSites=allSites, hint=hint)

            #If things are alright


            try:
                cursor.callproc("create_appointment",[siteName,date,time])
            except pymysql.IntegrityError or KeyError as e:
                return "unable to create appointment beacuse "+str(e)
            else:

                #Commit to the procedure call
                mysql.connection.commit()
                return render_template('createAppointment.html', allSites=allSites, hint ="You have successfully create an Appointment")

        else:
            return "Sorry you don't have the access to this screen"


#Screen 13a View Appointments
@app.route('/viewAppointment',methods=['GET','POST'])
def viewAppointment():
    global filter_data
    global reverse
    if request.method =='GET':
        if 'user' in session and (session['userPerms'] == 'Admin' or session['userPerms'] == 'Tester' or session['userPerms'] == "LabTech+Tester"):
            cursor = mysql.connection.cursor()
            sql = "select site_name from SITE"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall();
            allSites = []
            for site in content:
                allSites.append(site[0])

            cursor.close()
            filter_data = {"Site": "None", "StartDate": "None", "EndDate": "None", "StartTime": "None",
                           "EndTime": "None", "Availability": "None"}

            return render_template('viewAppointment.html', allSites=allSites, filter_data = filter_data)
        else:
            return "Sorry you don't have the access to this screen"


    elif request.method == 'POST':
        if 'user' in session and (session['userPerms'] == 'Admin' or session['userPerms'] == 'Tester'):
            labels = ['Date', 'Time', 'test Site', 'Location', 'User']
            #GET also need to work here:
            cursor = mysql.connection.cursor()
            sql = "select site_name from SITE"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall();
            allSites = []
            for site in content:
                allSites.append(site[0])



            cursor = mysql.connection.cursor()
            siteName = None if request.form.get('siteName') == '' else request.form.get('siteName')
            startDate = None if request.form.get('DateStart') == '' else request.form.get('DateStart')
            endDate = None if request.form.get('DateEnd') == '' else request.form.get('DateEnd')
            startTime = None if request.form.get('TimeStart') == '' else request.form.get('TimeStart')
            endTime = None if request.form.get('TimeEnd') == '' else request.form.get('TimeEnd')
            avail = request.form.get('Availability')

            if avail == 'booked':
                avail = 0
            elif avail == 'available':
                avail = 1
            elif avail == 'all':
                avail = None

            try:
                cursor.callproc("view_appointments",[siteName,startDate,endDate,startTime,endTime,avail])
            except pymysql.IntegrityError or KeyError as e:
                return "unable to view because " + str(e)
            else:
                #print the view to the html

                # select from the student_view_results_result
                sql = "select * from view_appointments_result"
                cursor.execute(sql)
                mysql.connection.commit()
                content = cursor.fetchall()

                # get the field name
                sql = "SHOW FIELDS FROM view_appointments_result"
                cursor.execute(sql)
                mysql.connection.commit()


                if avail == 0:
                    avail = "Booked"
                elif avail == 1:
                    avail = "Available"
                elif avail == None:
                    avail = "All"

                filter_data = {"Site":siteName,"StartDate":startDate,"EndDate":endDate,"StartTime":startTime,"EndTime":endTime,"Availability":avail}



                return render_template('viewAppointment.html', labels=labels, content=content, allSites=allSites, filter_data=filter_data)
        else:
            return "Sorry you don't have the access to this screen"



#Screen 14a: View Testers results(This need to be combined with assigned testers)
#Admin to assign or reassign testers to testing sites.
@app.route('/viewTester',methods=['GET','POST'])
def viewTester():
    if request.method =='GET':
        if 'user' in session and (session['userPerms'] == 'Admin'):
            cursor = mysql.connection.cursor()

            try:
                cursor.callproc("view_testers")
            except pymysql.IntegrityError or KeyError as e:
                return "unable to view because " + str(e)
            else:
                #print the view to the html
                # select from the student_view_results_result
                sql = "select * from view_testers_result"
                cursor.execute(sql)
                mysql.connection.commit()
                content = cursor.fetchall()

                testers = []
                for entry in content:
                    testers.append(entry[0])

                unassignedSites = []
                assignedSites = []
                for tester in testers:
                    try:
                        result = cursor.callproc("tester_assigned_sites",[tester])
                    except pymysql.IntegrityError or KeyError as e:
                        return "unable to view because " + str(e)
                    else:
                        sql = "select * from tester_assigned_sites_result"
                        cursor.execute(sql)
                        mysql.connection.commit()
                        assignedSitesInLoop = cursor.fetchall()
                        sql = "select site_name from site where site_name not in (select * from tester_assigned_sites_result)"
                        cursor.execute(sql)
                        mysql.connection.commit()
                        unassignedSitesInLoop = cursor.fetchall()
                        unassignedSites.append(unassignedSitesInLoop)
                        assignedSites.append(assignedSitesInLoop)

                # get the field name
                labels = ['Username','Name','Phone Number','Assigned Sites']



                return render_template('viewTester.html', labels=labels, content=content, unassignedSites = unassignedSites, assignedSites = assignedSites)
        else:
            return "Sorry You don't have the access to this screen"
    elif request.method == 'POST':
        if 'user' in session and (session['userPerms'] == 'Admin'):
            cursor = mysql.connection.cursor()
            #get the username
            usernames = request.form.getlist("Username")
            for i in range(len(usernames)):
                username = usernames[i]
                current = request.form.getlist(str(i)+"assigned")

                #The original sites：
                try:
                    cursor.callproc("tester_assigned_sites", [username])
                except pymysql.IntegrityError or KeyError as e:
                    return "unable to view because " + str(e)
                else:
                    mysql.connection.commit()

                try:
                    sql = "select * from tester_assigned_sites_result"
                    cursor.execute(sql)
                    mysql.connection.commit()
                    originalSites = []
                    content = cursor.fetchall()
                except pymysql.IntegrityError or KeyError as e:
                    return "unable to view because " + str(e)
                else:

                    for each in content:
                        originalSites.append(each[0])

                    #to see which part is unchecked now
                    uncheck = []
                    for ori in originalSites:
                        if ori not in current:
                            uncheck.append(ori)

                    #cancle each unchecked site
                    for unSite in uncheck:
                        try:
                            cursor.callproc("unassign_tester",[username,unSite])
                        except pymysql.IntegrityError or KeyError as e:
                            return "unable to view because " + str(e)
                        else:
                            mysql.connection.commit()

                            ##For test here
                            cursor.callproc("tester_assigned_sites", [username])
                            sql = "select * from tester_assigned_sites_result"
                            cursor.execute(sql)
                            mysql.connection.commit()
                            assignedSitesInLoop = cursor.fetchall()

                    # Now do the assigned part

                    newSite = request.form.get(str(i) + "siteNameAdd")#Safely assumes we can only add one site once
                    try:
                        cursor.callproc("assign_tester", [username, newSite])
                    except pymysql.IntegrityError or KeyError as e:
                        return "unable to view because " + str(e)
                    else:
                        mysql.connection.commit()

             #Update the view here(This code is really long)
            cursor = mysql.connection.cursor()

            try:
                cursor.callproc("view_testers")
            except pymysql.IntegrityError or KeyError as e:
                return "unable to view because " + str(e)
            else:
                #print the view to the html
                # select from the student_view_results_result
                sql = "select * from view_testers_result"
                cursor.execute(sql)
                mysql.connection.commit()
                content = cursor.fetchall()

                testers = []
                for entry in content:
                    testers.append(entry[0])

                unassignedSites = []
                assignedSites = []
                for tester in testers:
                    try:
                        result = cursor.callproc("tester_assigned_sites",[tester])
                    except pymysql.IntegrityError or KeyError as e:
                        return "unable to view because " + str(e)
                    else:
                        sql = "select * from tester_assigned_sites_result"
                        cursor.execute(sql)
                        mysql.connection.commit()
                        assignedSitesInLoop = cursor.fetchall()
                        sql = "select site_name from site where site_name not in (select * from tester_assigned_sites_result)"
                        cursor.execute(sql)
                        mysql.connection.commit()
                        unassignedSitesInLoop = cursor.fetchall()
                        unassignedSites.append(unassignedSitesInLoop)
                        assignedSites.append(assignedSitesInLoop)

                # get the field name
                labels = ['Username','Name','Phone Number','Assigned Sites']

                return render_template('viewTester.html', labels=labels, content=content, unassignedSites = unassignedSites, assignedSites = assignedSites)
        else:
            return "Sorry you don't have the access to this screen"


#Screen 15a:  Create a Testing Site
@app.route('/createTestSite',methods=['GET','POST'])
def createTestSite():
    if request.method =='GET':
        if 'user' in session and (session['userPerms'] == 'Admin'):
            cursor = mysql.connection.cursor()
            #This is the Lname and Fname for selection
            sql = "select concat(concat(fname,' '),lname) as name from User where USER.username in (select sitetester_username from SITETESTER)"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall()
            allTesters = []
            for tester in content:
                allTesters.append(tester[0])

            #Now is the username for each value
            sql = "select sitetester_username from SITETESTER"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall()
            allUsernames = []
            for tester in content:
                allUsernames.append(tester[0])

            cursor.close()
            hint = "You don't have last Operation"
            return render_template('createTestSite.html', allTesters=allTesters, allUsernames = allUsernames, hint=hint)
        else:
            return "Sorry you don't have the access to this screen"
    elif request.method == 'POST':
        if 'user' in session and (session['userPerms'] == 'Admin'):
            #Some visualizaiton stuff
            cursor = mysql.connection.cursor()
            # This is the Lname and Fname for selection
            sql = "select concat(concat(fname,' '),lname) as name from User where USER.username in (select sitetester_username from SITETESTER)"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall()
            allTesters = []
            for tester in content:
                allTesters.append(tester[0])

            # Now is the username for each value
            sql = "select sitetester_username from SITETESTER"
            cursor.execute(sql)
            mysql.connection.commit()
            content = cursor.fetchall()
            allUsernames = []
            for tester in content:
                allUsernames.append(tester[0])



            cursor = mysql.connection.cursor()
            site = request.form.get("Site")
            address = request.form.get("Address")
            city = request.form.get("City")
            state = request.form.get("State")
            zipCode = request.form.get("Zip")
            location = request.form.get("Location")
            tester = request.form.get("Tester")
            try:
                sql = "select * from SITE where site_name = %s"

            except pymysql.IntegrityError or KeyError as e:
                return "unable to create because " + str(e)
            else:
                cursor.execute(sql,(site))
                mysql.connection.commit()
                exist = cursor.fetchall()
                if len(exist) !=0:
                    hint = "Sorry this site already exist, Please re-enter another sitename"
                    return render_template('createTestSite.html', allTesters=allTesters, allUsernames=allUsernames, hint=hint)

            try:
                cursor.callproc("create_testing_site",[site,address,city,state,zipCode,location,tester])
            except pymysql.IntegrityError or KeyError as e:
                return "unable to create because " + str(e)
            else:
                mysql.connection.commit()
                hint = "Successfully Created"
                return render_template('createTestSite.html', allTesters=allTesters, allUsernames = allUsernames, hint=hint)
        else:
            return "Sorry you don't have the access to this screen"


#Screen 16a: Explore Pool Result & 16b

@app.route('/poolResult/<id>',methods=['GET'])
def poolMetaDate(id):

    cursor = mysql.connection.cursor()

    try:
        cursor.callproc("pool_metadata",[id])

    except pymysql.IntegrityError or KeyError as e:
        return "unable to view because " + str(e)
    else:
        #print the view to the html

        # select from the student_view_results_result
        sql = "select * from pool_metadata_result"
        cursor.execute(sql)
        mysql.connection.commit()
        content = cursor.fetchall()

        # get the field name
        sql = "SHOW FIELDS FROM pool_metadata_result"
        cursor.execute(sql)
        mysql.connection.commit()
        labels = ['Pool ID','Date Processed','Pooled Result','ProcessedBy']


        labels_two = ['Test ID', 'Date Tested', 'Testing Site', 'Test Result']

        cursor.callproc('tests_in_pool',[id])
        sql = "select * from tests_in_pool_result"
        cursor.execute(sql)
        mysql.connection.commit()
        content_two = cursor.fetchall()



        return render_template('poolResult.html', labels=labels, content=content, labels_two = labels_two, content_two = content_two)

#Screen 18a: View Daily Results
@app.route('/dailyresults')
def dailyresults():
    cursor = mysql.connection.cursor()
    try:
        result = cursor.callproc("daily_results")
    except pymysql.IntegrityError or KeyError as e:
            return "unable to view because " + str(e)
    else:
        sql = "select * from daily_results_result"
        cursor.execute(sql)
        mysql.connection.commit()
        content = cursor.fetchall()

        labels = ['Date', 'Tests Processed', 'Positive Count', 'Positive Percent']

        return render_template('dailyresults.html', labels=labels, content=content)



if __name__ == '__main__':
    app.run(debug=True)
