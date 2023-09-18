from flask import render_template, make_response
from flask import redirect, flash
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
from config import *
import datetime
import logging
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


@app.route('/adminLogin', methods=['POST', 'GET'])
def adminLogin():
    return render_template('adminLogin.html')

@app.route('/adminViewContactUs', methods=['POST'])
def adminContactUs():
    email = request.form.get('email')
    password = request.form.get('password')

    if email == 'hhm@gmail.com' and password == '123':
        session['name'] = 'Ho Hong Meng'
        session['loggedIn'] = 'hhm'
        return render_template('adminContactUs.html', name=session['name'])

    elif email == 'css@gmail.com' and password == '456':
        session['name'] = 'Cheong Soo Siew'
        session['loggedIn'] = 'css'
        return render_template('adminContactUs.html', name=session['name'])

    else:
        error_msg = 'Invalid email or password. Please try again.'
        return render_template('adminLogin.html', msg=error_msg)

# @app.route('/adminViewContact', methods=['POST'])
# def adminViewContact():


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
