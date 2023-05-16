import base64
import io
import json
import os
import csv
from datetime import datetime
from flask import Flask, redirect, render_template, request, session, make_response
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

# Delete the session cookie file if it exists

session_cookie_path = './session_cookie'
if os.path.exists(session_cookie_path):
    os.remove('flask_session')

app = Flask(__name__, template_folder='./html_files')


# Set the location of the session cookie file to a temporary directory
app.config['SESSION_FILE_DIR'] = './'
app.config['SESSION_FILE_THRESHOLD'] = 0
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SECRET_KEY'] = os.urandom(24)


# Load the user data from the JSON file
with open('users.json') as f:
    users = json.load(f)

# Main page: if user connected you go to dashboard, otherwise go to login
@app.route('/')
def index():
    if 'username' in session:
        print(session)
        return redirect('/dashboard')
    else:
        session.pop('username', None)
        return redirect('/login')


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error message to None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password: # Check username and password are correct
            session['username'] = username  # Store the username in a session variable
            return redirect('/dashboard')
        else:
            error = "Invalid login credentials. Please try again."  # Set error message, which will appear in the html
    return render_template('login.html', error=error)  # Pass error message to the template


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None  # Initialize error message to None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users: # Username exists -> error
            error = "Username already exists. Please choose a different one."  # Set error message
        else: # Create username 
            # Update the user data in the JSON file
            users[username] = password
            with open('users.json', 'w') as f:
                json.dump(users, f)
            session['username'] = username  # Store the username in a session variable
            return redirect('/dashboard')
    return render_template('registration.html', error=error)  # Pass error message to the template

# Page with to access the input, track and recommendations pages
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect('/login')
    

# Questionnaire/Survey page
@app.route('/input', methods=['GET', 'POST'])
def input_data():
    if request.method == 'POST':
        answer1 = request.form['question1']
        answer2 = request.form['question2']
        answer3 = request.form['question3']
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        with open('answers.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if os.stat('answers.csv').st_size == 0: # write header if file is empty
                writer.writerow(['username', 'datetime', 'question1', 'question2', 'question3'])
            writer.writerow([session['username'], current_time, answer1, answer2, answer3])
        return redirect('/track')
    
    return render_template('input.html')

# Tracking data page, with the graphs and any required tracking data tool
@app.route('/track')
def track_data():
    # Get the data for the current user from the answers.csv file
    username = session['username']
    data = pd.read_csv('answers.csv')
    user_data = data[data['username'] == username]

    # Create a dictionary to store the data for each date
    dates = sorted(list(set(user_data['datetime'])))
    date_data = {date: {'q1': [], 'q2': [], 'q3': []} for date in dates}

    # Extract the data for each date
    for _, row in user_data.iterrows():
        date = row['datetime']
        date_data[date]['q1'].append(row['question1'])
        date_data[date]['q2'].append(row['question2'])
        date_data[date]['q3'].append(row['question3'])

    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()

    # Plot the data for each date and connect the points
    for date in dates:
        x = ['Q1', 'Q2', 'Q3']
        y = [np.mean(date_data[date]['q1']),
             np.mean(date_data[date]['q2']),
             np.mean(date_data[date]['q3'])]
        ax.plot(x, y, label=date, marker='o')
        ax.plot(x, y, 'k--', alpha=0.5)

    ax.set_xlabel('Question')
    ax.set_ylabel('Answer')
    ax.legend()

    # Save the figure to a temporary buffer.
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Embed the result in the html output.
    data = base64.b64encode(buf.getvalue()).decode()
    return render_template('track.html', plot_url=f'data:image/png;base64,{data}')

# Recommendations page
@app.route('/recommend')
def recommend_data():
    return render_template('recommend.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)