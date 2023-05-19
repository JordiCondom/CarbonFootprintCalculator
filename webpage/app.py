import base64
import io
import os
import csv
from datetime import datetime
from flask import Flask, redirect, render_template, request, session, make_response
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from classes.mongodbmanager import MongoDBManager
import psycopg2
from psycopg2 import sql

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

# Main page: if user connected you go to dashboard, otherwise go to login
@app.route('/')
def index():
    if 'username' in session:
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
        mongo_manager = MongoDBManager('CarbonFootprintCalculator', 'Users')
        if mongo_manager.check_login(username, password):
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
        repeat_password = request.form['repeat_password']
        mongo_manager = MongoDBManager('CarbonFootprintCalculator', 'Users')

        if mongo_manager.users_collection.find_one({'username': username}): # Username exists -> error
            error = "Username already exists. Please choose a different one."  # Set error message
        elif password != repeat_password:
            error = "Password not matching"
        else: # Create username 
            # Update the user data in the JSON file
            user = {
                'username': username,
                'password': password
            }
            
            mongo_manager.insert_user(user)
            
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
        answer4 = request.form['question4']
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        conn = psycopg2.connect(
            host='localhost',
            port=5858,
            user='postgres',
            password='password',
            database='mydatabase'
        )
        
        '''
        conn = psycopg2.connect(
            host='postgres',
            port='5432',
            user='postgres',
            password='password',
            database='mydatabase'
        )
        '''
        # Retrieve the username from the Flask session
        username = session['username']
        
        # Create a table name based on the username
        table_name = f'user_{username}'
        
        # Create the table if it doesn't exist
        with conn.cursor() as cursor:
            create_table_query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    datetime TIMESTAMP,
                    question1 INTEGER,
                    question2 INTEGER,
                    question3 INTEGER,
                    question4 INTEGER,
                    total INTEGER
                )
            """).format(table_name=sql.Identifier(table_name))
            cursor.execute(create_table_query)
        
        # Insert the data into the table
        with conn.cursor() as cursor:
            insert_query = sql.SQL("""
                INSERT INTO {table_name} (datetime, question1, question2, question3, question4, total)
                VALUES (%s, %s, %s, %s, %s, %s)
            """).format(table_name=sql.Identifier(table_name))
            cursor.execute(insert_query, (current_time, answer1, answer2, answer3, answer4, int(answer1) + int(answer2) + int(answer3) + int(answer4)))
        
        # Commit the transaction
        conn.commit()
        
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
    date_data = {date: {'food': [], 'transportation': [], 'household': [], 'expenses': [], 'total': []} for date in dates}

    # Extract the data for each date
    for _, row in user_data.iterrows():
        date = row['datetime']
        date_data[date]['food'].append(row['food'])
        date_data[date]['transportation'].append(row['transportation'])
        date_data[date]['household'].append(row['household'])
        date_data[date]['expenses'].append(row['expenses'])
        date_data[date]['total'].append(row['total'])

    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=(10, 10))
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    # Plot the data for each date and connect the points
    for date in dates:
        x = ['food', 'transportation', 'household', 'expenses']
        y = [np.mean(date_data[date]['food']),
             np.mean(date_data[date]['transportation']),
             np.mean(date_data[date]['household']),
             np.mean(date_data[date]['expenses'])]
        ax1.plot(x, y, label=date, marker='o')
        ax1.plot(x, y, 'k--', alpha=0.5)

    ax1.set_xlabel('Question')
    ax1.set_ylabel('Answer')
    ax1.legend()

    # Create a pie chart for the expense categories
    expense_labels = ['Food', 'Transportation', 'Household', 'Expenses']
    expense_values = [
        np.sum(user_data['food']),
        np.sum(user_data['transportation']),
        np.sum(user_data['household']),
        np.sum(user_data['expenses'])
    ]
    ax2.pie(expense_values, labels=expense_labels, autopct='%1.1f%%')
    ax2.set_aspect('equal')  # Equal aspect ratio ensures the pie is circular

    ax3.plot(user_data['datetime'], user_data['total'])
    ax3.set_xlabel('Datetime')
    ax3.set_ylabel('Total')

    # Save the figures to a temporary buffer.
    buf1 = io.BytesIO()
    fig.savefig(buf1, format='png')
    buf1.seek(0)

    # Embed the results in the HTML output.
    data1 = base64.b64encode(buf1.getvalue()).decode()
    return render_template('track.html', plot_url1=f'data:image/png;base64,{data1}')

# Recommendations page
@app.route('/recommend')
def recommend_data():
    return render_template('recommend.html')


if __name__ == '__main__':
    app.run(debug=True)
