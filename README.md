# Screens Description
note: the front-end styling is only for reference now.

##DashBoard for different users
![campgrounds](https://github.com/hongyuchen1030/YelpCamp/blob/master/readmeImage/campgrounds.png?raw=true)












# Setup Instruction: 

Requires MySQL server running on local machine. 

Requires a Python3 installation, with packages: 

click==7.1.2 

Flask==1.1.2 

Flask-MySQLdb==0.2.0 

itsdangerous==1.1.0 

Jinja2==2.11.2 

MarkupSafe==1.1.1 

mysqlclient==2.0.1 

numpy==1.19.3 

PyMySQL==0.10.1 

Werkzeug==1.0.1 



Potential issues occur when attempting install of flask-mysqldb on MacOS, one possible solution: 

export PATH=$PATH:/usr/local/mysql/bin  

pip3 install flask-mysqldb 

 

Alternatively, one can utilize the virtual environments pre-made in the zip file. \venv for Mac

Run Instructions: 

Database 

Start a local MySQL Server 

Run the file db_init.sql 

Run the file procedureBank.sql 


Web-App 

Navigate to the folder \FlaskDemo 

Within the file “app.py”, change the lines (23, 24)  

app.config[‘MYSQL_USER’] 

app.config[‘MYSQL_PASSWORD’]  

to credentials with appropriate privilege on your MySQL server 

Open a terminal within the \FlaskDemo folder 

Run the command “flask run” 

Navigate to the given web address on a web browser 

 

 

 

Technologies: 

We used Python with the Flask framework to create the core-backend for the website, creating the base web-app. In order to build the frontend to this webapp, we utilized Bootstrap with HTML and CSS, including the extension Bootstrap Table. From there, we utilized flask_mysqldb in order to connect the Flask app with our locally hosted mySQL database. User logins were handled via sessions in Flask, enabling us to return specific webpages depending on the type of user logged in. User duplication detection are handled both in the front-end and the backend database to prevent primary key errors and the same user registers in the system more than once 

 

Distribution of work: 

Hongyu: Handled screens 12, 13, 14, 15, 16a, as well as user registration/user-duplication-identification and interaction between frontend and backend including frontend table display.

Yingnan: Handled screens 4, 5, 6, 7, 8, 9 as well as sortable tables and part of front-end files 

Rebecca: Created the front-end HTML/CSS/Bootstrap 

Zilong: Handled screens 10, 11, 16b, 17, and 18, as well as the base Flask app and login/sessions specifics, and Bootstrap Table.

 

 

 

 

 
