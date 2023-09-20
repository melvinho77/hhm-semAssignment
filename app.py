from flask import render_template, make_response
from flask import redirect, flash
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
from config import *
import socket


app = Flask(__name__)
app.static_folder = 'static'  # The name of your static folder
app.static_url_path = '/static'  # The URL path to serve static files
app.secret_key = 'cc'

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
table = 'focsWebsite'


@app.route('/')
def index():
    network_details = get_network_details()
    return render_template('home.html', number=1, network_details=network_details)


def get_network_details():
    try:
        # Get the host name of the local machine
        host_name = socket.gethostname()

        # Get both IPv4 and IPv6 addresses associated with the host
        ipv4_address = socket.gethostbyname(host_name)
        ipv6_address = socket.getaddrinfo(
            host_name, None, socket.AF_INET6)[0][4][0]

        return {
            'Host Name': host_name,
            'IPv4 Address': ipv4_address,
            'IPv6 Address': ipv6_address
        }
    except Exception as e:
        return {'Error': str(e)}


@app.route("/contactUs")
def contact_us():
    # Call the get_network_details function to retrieve network details
    network_details = get_network_details()

    # Pass the network_details and msg to the contactUs.html template
    return render_template("contactUs.html", network_details=network_details)


@app.route("/trackContactUs")
def trackContactUs():
    # Change to session data
    student = '2'
    session['loggedInStudent'] = '2'
    network_details = get_network_details()

    # Retrieve all contact data based on this student
    select_sql = "SELECT * FROM contact WHERE student = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (student))
        contact_data = cursor.fetchall()
        db_conn.commit()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    return render_template("studentContactUs.html", contact_data=contact_data, student=session['loggedInStudent'], network_details=network_details)


@app.route('/submitContactUs', methods=['POST'])
def submitContactUs():
    # After log in, then only can ask question
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    category = request.form.get('category')
    inquiries = request.form.get('inquiries')

    try:
        insert_sql = "INSERT INTO contact (`status`, category, question, reply, repliedBy, student) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        cursor.execute(insert_sql, ('pending', category,
                       inquiries, None, None, student_id))
        db_conn.commit()

        # Flash a success message
        flash('Question submitted successfully', 'success')

        # Redirect back to the contactUs page
        return redirect('/contactUs')

    except Exception as e:
        db_conn.rollback()
        return str(e)


@app.route('/adminLogin')
def adminLogin():
    network_details = get_network_details()
    return render_template('adminLogin.html', network_details=network_details)


@app.route('/adminContactUs', methods=['POST', 'GET'])
def adminContactUs():
    # Handle the form submission with email and password
    email = request.form.get('email')
    password = request.form.get('password')

    if email == 'hhm@gmail.com' and password == '123':
        session['name'] = 'Ho Hong Meng'
        session['loggedIn'] = 'hhm'

    elif email == 'css@gmail.com' and password == '456':
        session['name'] = 'Cheong Soo Siew'
        session['loggedIn'] = 'css'

    network_details = get_network_details()

    try:
        cursor = db_conn.cursor()
        # Retrieve contact details for the current page
        cursor.execute("SELECT * FROM contact")
        contactDetails = cursor.fetchall()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    if request.method == 'POST':

        if email == 'hhm@gmail.com' and password == '123':
            return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

        elif email == 'css@gmail.com' and password == '456':
            return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

        else:
            error_msg = 'Invalid email or password. Please try again.'
            return render_template('adminLogin.html', msg=error_msg, network_details=network_details)

    return render_template(
        'adminContactUs.html',
        name=session['name'],
        contact_details=contactDetails,
        network_details=network_details
    )


@app.route('/replyQuestion', methods=['POST', 'GET'])
def replyQuestion():
    contactId = request.form.get('contactId')
    reply = request.form.get('reply')
    repliedBy = session['name']

    # Update the contact us details
    update_sql = "UPDATE contact SET reply = %s, repliedBy = %s, status=%s WHERE contactId = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (reply, repliedBy, 'completed', contactId))
        db_conn.commit()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    if 'name' in session and 'email' in session:
        name = session['name']
        email = session['email']
        if email == 'hhm@gmail.com' and name == 'Ho Hong Meng':
            session['loggedIn'] = 'hhm'
        elif email == 'css@gmail.com' and name == 'Cheong Soo Siew':
            session['loggedIn'] = 'css'

    # Flash a success message
    flash('Question submitted successfully', 'success')

    # Redirect back to the contactUs page
    return redirect('/adminContactUs')


@app.route('/applyFilter', methods=['POST', 'GET'])
def applyFilter():
    # Extract filter criteria from the form
    category = request.form.get('category')
    status = request.form.get('status')
    network_details = get_network_details()

    try:
        # Create a cursor
        cursor = db_conn.cursor()

        # Construct the SQL query based on the selected filters
        sql = "SELECT * FROM contact WHERE 1=1"

        if category != '*':
            sql += f" AND category = '{category}'"
        if status != '*':
            sql += f" AND status = '{status}'"

        cursor.execute(sql)

        # Fetch the filtered data
        contact_details = cursor.fetchall()

        if 'name' in session and 'email' in session:
            name = session['name']
            email = session['email']
            if email == 'hhm@gmail.com' and name == 'Ho Hong Meng':
                session['loggedIn'] = 'hhm'
                session['loggedInName'] = 'Ho Hong Meng'
            elif email == 'css@gmail.com' and name == 'Cheong Soo Siew':
                session['loggedIn'] = 'css'
                session['loggedInName'] = 'Cheong Soo Siew'

        return render_template('adminContactUs.html', contact_details=contact_details, network_details=network_details, name=session['loggedInName'])

    except Exception as e:
        db_conn.rollback()
        return str(e)


@app.route('/studentApplyFilter', methods=['POST', 'GET'])
def studentApplyFilter():
    # Extract filter criteria from the form
    category = request.form.get('category')
    status = request.form.get('status')
    network_details = get_network_details()

    try:
        # Create a cursor
        cursor = db_conn.cursor()

        # Construct the SQL query based on the selected filters
        sql = "SELECT * FROM contact WHERE 1=1 AND student = %s"

        if category != '*':
            sql += f" AND category = '{category}'"
        if status != '*':
            sql += f" AND status = '{status}'"

        cursor.execute(sql, ('2'))

        # Fetch the filtered data
        contact_details = cursor.fetchall()

        return render_template('studentContactUs.html', contact_details=contact_details, network_details=network_details)

    except Exception as e:
        db_conn.rollback()
        return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
