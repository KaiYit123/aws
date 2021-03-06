from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__,template_folder="templates",static_folder= 'templates/static')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/homepage")
def homepage():
    return render_template('index.html')

@app.route("/add")
def Add():
    return render_template('AddEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/view")
def view():
    return render_template('GetEmp.html')

@app.route("/getemppayroll")
def getemppayroll():
    return render_template('GetEmpPayRoll.html')

@app.route("/getviewemppayroll")
def getviewemppayroll():
    return render_template('GetViewEmpPayRoll.html')

@app.route("/viewemppayroll", methods=['POST'])
def viewemppayroll():
    emp_id = request.form['emp_id']

    select_sql = "SELECT * FROM payroll WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql,(emp_id))
    db_conn.commit()
    emp = cursor.fetchone()
    cursor.close()
    return render_template('ViewEmpPayRoll.html', emp = emp)


@app.route("/getemppayrolltoedit", methods=['POST'])
def getemppayrolltoedit():
    emp_id = request.form['emp_id']

    select_sql = "SELECT * FROM payroll WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql,(emp_id))
    db_conn.commit()
    emp = cursor.fetchone()
    cursor.close()
    return render_template('EditEmpPayRoll.html', emp = emp)

@app.route("/updateemppayroll", methods=['POST','GET'])
def updateemppayroll():
    emp_id = request.form['emp_id']
    salary = request.form['salary']
    epf = request.form['epf']
    socso = request.form['socso']
    tax = request.form['tax']
    net = request.form['net']

    update_sql = "UPDATE payroll SET salary=%s, epf=%s, socso=%s,tax=%s, net=%s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql,(salary,epf,socso,tax,net,emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()
    return render_template('EditEmpPayRollOutput.html', id = emp_id)

@app.route("/edit")
def edit():
    return render_template('GetEmpEdit.html')

@app.route("/fetchdataforedit", methods=['POST'])
def fetchdataforedit():
    emp_id = request.form['emp_id']

    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql,(emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()
    return render_template('EditEmp.html', user = user)

@app.route("/update", methods=['POST','GET'])
def update():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    update_sql = "UPDATE employee SET first_name=%s, last_name=%s, pri_skill=%s,location=%s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql,(first_name,last_name,pri_skill,location,emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()
    return render_template('EditEmpOutput.html', id = emp_id)

@app.route("/delete")
def delete():
    return render_template('GetEmpDelete.html')

@app.route("/fetchdata", methods=['POST'])
def fetchdata():
    emp_id = request.form['emp_id']

    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql,(emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()
    return render_template('GetEmpOutput.html', user = user)

@app.route("/fetchdatafordelete", methods=['POST'])
def fetchdatafordelete():
    emp_id = request.form['emp_id']

    delete_sql = "DELETE FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(delete_sql,(emp_id))
    db_conn.commit()
    user = cursor.fetchone()
    cursor.close()
    return render_template('DelEmpOutput.html', id = emp_id)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    hire_date = request.form['hire_date']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:


        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file" + ".jpg"
        emp_url = "https://hongkaiyit-bucket.s3.amazonaws.com/" + emp_image_file_name_in_s3
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, hire_date, emp_url))
        db_conn.commit()
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/payroll")
def payroll():
    return render_template('AddPayRoll.html')

@app.route("/addpayroll", methods=['POST'])
def addpayroll():
    emp_id = request.form['emp_id']
    salary = request.form['salary']
    epf = request.form['epf']
    socso = request.form['socso']
    tax = request.form['tax']
    net = request.form['net']

    insert_sql = "INSERT INTO payroll VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    cursor.execute(insert_sql, (emp_id, salary, epf, socso, tax, net))
    db_conn.commit()
    cursor.close()            
    
    return render_template('AddPayRollOutput.html', emp=emp_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
