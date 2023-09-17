from flask import render_template, make_response
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
from config import *
import datetime
import logging, socket

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

# N8 - Retrieve network details
def get_network_details():
    try:
        # Get the host name of the local machine
        host_name = socket.gethostname()

        # Get both IPv4 and IPv6 addresses associated with the host
        ipv4_address = socket.gethostbyname(host_name)
        ipv6_address = socket.getaddrinfo(host_name, None, socket.AF_INET6)[0][4][0]

        return {
            'Host Name': host_name,
            'IPv4 Address': ipv4_address,
            'IPv6 Address': ipv6_address
        }
    except Exception as e:
        return {'Error': str(e)}

@app.route('/contactUs')
def contact_us():
    # Call the get_network_details function to retrieve network details
    network_details = get_network_details()

    # Pass the network_details to the contactUs.html template
    return render_template('contactUs.html', network_details=network_details)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
