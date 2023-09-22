from flask import render_template, make_response, jsonify, flash
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
import socket
from config import *
import datetime
import difflib
# from weasyprint import HTML

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
table = 'employee'


@app.route('/home_page')
def home_page():
    return render_template('home.html')


@app.route('/')
def index():
    network_details = get_network_details()
    return render_template('home.html', number=1, network_details=network_details)


@app.route("/", methods=['GET', 'POST'])
def home():
    network_details = get_network_details()
    return render_template('home.html', network_details=network_details)

# req1


@app.route('/relevantResult_display', methods=['POST'])
def relevantResult_display():
    result = request.form['result']
    network_details = get_network_details()
    return render_template(result, network_details=network_details)

# req1


@app.route('/homeSearchProgramme', methods=['POST'])
def homeSearchProgramme():
    searchObj = request.form['textInput']
    network_details = get_network_details()

    select_sql = f"SELECT * FROM availableProgramme"
    cursor = db_conn.cursor()
    cursor.execute(select_sql)
    searchRange = cursor.fetchall()

    url_set = {
        1: "programmes/Diploma in Computer Science.html",
        2: "programmes/Diploma in Information Systems.html",
        3: "programmes/Diploma in Information Technology.html",
        4: "programmes/Diploma in Software Engineering.html",
        5: "programmes/Management Mathematics with Computing.html",
        6: "programmes/Interactive Software Technology.html",
        7: "programmes/Data Science.html",
        8: "programmes/Enterprise Information Systems.html",
        9: "programmes/Information Security.html",
        10: "programmes/Internet Technology.html",
        11: "programmes/Software Systems Development.html",
        12: "programmes/Software Engineering.html",
        13: "programmes/Master of Computer Science.html",
        14: "programmes/Master of Information Technology.html",
        15: "programmes/Master of Science in Mathematical Sciences.html",
        16: "programmes/Doctor of Philosophy Computer Science.html",
        17: "programmes/Doctor of Philosophy Information Technology.html",
        18: "programmes/Doctor of Philosophy Mathematical Sciences.html"
    }

    similarity_scores = []

    # Iterate through the program names in 'searchRange'
    for program in searchRange:
        program_id = program[0]
        program_name = program[1]
        similarity = difflib.SequenceMatcher(
            None, searchObj, program_name).ratio()

        if similarity > 0.1:
            similarity_scores.append((program_id, program_name, similarity))

    # Sort the results by similarity in descending order
    sorted_similarity_scores = sorted(
        similarity_scores, key=lambda x: x[2], reverse=True)

    # Get the top 5 most relevant results
    top_5_results = sorted_similarity_scores[:5]

    relevantResults = []
    if not top_5_results:
        return render_template('relevantProgrammeSearchResult.html', relevantResults=relevantResults, network_details=network_details)
    else:
        for element in top_5_results:
            count = 0
            for url in url_set:
                count += 1
                if count == element[0]:
                    relevantResults.append(url_set.get(count))
        print(relevantResults)
        return render_template('relevantProgrammeSearchResult.html', relevantResults=relevantResults, network_details=network_details)

# N8 - Retrieve network details


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

# N10 - Trace contact details


@app.route("/contactUs")
def contact_us():
    # Call the get_network_details function to retrieve network details
    network_details = get_network_details()

    # Flash a success message
    flash('Question submitted successfully', 'success')

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
    network_details = get_network_details()
    # Handle the form submission with email and password
    email = request.form('email')
    password = request.form('password')

    try:
        cursor = db_conn.cursor()
        # Retrieve contact details for the current page
        cursor.execute("SELECT * FROM contact")
        contactDetails = cursor.fetchall()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    if email == 'hhm@gmail.com' and password == '123':
        session['name'] = 'Ho Hong Meng'
        session['loggedIn'] = 'hhm'
        return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

    elif email == 'css@gmail.com' and password == '456':
        session['name'] = 'Cheong Soo Siew'
        session['loggedIn'] = 'css'
        return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

    else:
        error_msg = 'Invalid email or password. Please try again.'
        return render_template('adminLogin.html', msg=error_msg, network_details=network_details)


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
            session['name'] = 'Ho Hong Meng'
        elif email == 'css@gmail.com' and name == 'Cheong Soo Siew':
            session['loggedIn'] = 'css'
            session['name'] = 'Cheong Soo Siew'

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
                session['name'] = 'Ho Hong Meng'
            elif email == 'css@gmail.com' and name == 'Cheong Soo Siew':
                session['loggedIn'] = 'css'
                session['name'] = 'Cheong Soo Siew'

        return render_template('adminContactUs.html', contact_details=contact_details, network_details=network_details, name=session['name'])

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

        return render_template('studentContactUs.html', contact_data=contact_details, network_details=network_details)

    except Exception as e:
        db_conn.rollback()
        return str(e)

@app.route('/logout')
def admin_logout():
    # Clear session data
    session.pop('name', None)
    session.pop('loggedIn', None)
    
    return redirect(url_for('adminLogin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
