from flask import render_template, make_response
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
from config import *
import datetime
import logging

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
    return render_template('home.html', number=1)


@app.route('/contactUs')
def contact_us():
    try:
        # Get the user's IP address from the request object
        user_ip = request.remote_addr

        # Get the user agent information from the request object
        user_agent = request.headers.get('User-Agent')

        # Get the client's host name using socket
        import socket
        host_name = socket.gethostbyaddr(user_ip)[0]

        # Log the details for debugging and auditing
        logging.info(
            f'User IP: {user_ip}, User-Agent: {user_agent}, Host Name: {host_name}')

        return render_template('contactUs.html', user_ip=user_ip, user_agent=user_agent, host_name=host_name)

    except Exception as e:
        # Log any errors or exceptions
        logging.error(f'Error occurred: {str(e)}')
        return render_template('error.html', error_message='An error occurred. Please try again later.')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
