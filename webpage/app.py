import base64
import io
import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, session, make_response
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from classes.graphcreator import graphCreator
from classes.mongodbmanager import MongoDBManager
import psycopg2
from psycopg2 import sql

from classes.postgresqlmanager import PostgreSQLManager
from classes.redismanager import RedisManager

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
@app.route('/dashboard',  methods=['GET', 'POST'])
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
        current_time = now.strftime("%Y-%m-%d %H:%M")

        postgresql_manager = PostgreSQLManager('localhost',5858,'postgres', 'password', 'mydatabase')
    
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
        columns = [
            'datetime TIMESTAMP',
            'question1 INTEGER',
            'question2 INTEGER',
            'question3 INTEGER',
            'question4 INTEGER',
            'total INTEGER',
        ]

        postgresql_manager.create_table(table_name, columns)
        
        input_data_columns = ['datetime', 'question1', 'question2', 'question3', 'question4', 'total']
        input_data_values = [current_time, answer1, answer2, answer3, answer4, int(answer1) + int(answer2) + int(answer3) + int(answer4)]

        postgresql_manager.insert_data(table_name, input_data_columns, input_data_values)
        
        return redirect('/track')
    
    return render_template('input.html')

@app.route('/track', methods=['GET', 'POST'])
def track_data():
    error = None
    graph_data = None
    username = session['username']
    redis_manager = RedisManager('localhost', 6379, 0)

    if request.method == 'POST':
        from_date = request.form.get('fromDate')
        to_date = request.form.get('toDate')
        key = str(username) + str(from_date) + str(to_date)
        if from_date > to_date:
            error = "Watch out, the start date is later than the end date!"
        else:
            if (redis_manager.key_exists_boolean(key)):
                graph_data = redis_manager.get_value_by_key(key)
                return render_template('track.html', plot_url1=f'data:image/png;base64,{graph_data}', error=error)
            else:
                # Get the data for the current user from the database
                postgresql_manager = PostgreSQLManager('localhost', 5858, 'postgres', 'password', 'mydatabase')
                user_data = postgresql_manager.get_data_from_date_range(f'user_{username}', from_date, to_date)

                if user_data:
                    df = pd.DataFrame(user_data, columns=['datetime', 'food', 'transportation', 'household', 'expenses', 'total'])

                    # Create a dictionary to store the data for each date
                    dates = sorted(list(set(df['datetime'])))
                    date_data = {date: {'food': [], 'transportation': [], 'household': [], 'expenses': [], 'total': []} for date in dates}

                    graph_manager = graphCreator(df, dates, date_data)
                    graph_data = graph_manager.create_tracking_graphs()
                    redis_manager.set_key_value(key, graph_data)

                    return render_template('track.html', plot_url1=f'data:image/png;base64,{graph_data}', error=error)
                else:
                    error = "No data available for this range of dates"

    # Get the data for the current user from the database
    username = session['username']
    postgresql_manager = PostgreSQLManager('localhost', 5858, 'postgres', 'password', 'mydatabase')
    user_data = postgresql_manager.get_all_data(f'user_{username}')

    if user_data:
        df = pd.DataFrame(user_data, columns=['datetime', 'food', 'transportation', 'household', 'expenses', 'total'])

        earliest_date = df['datetime'].min()
        latest_date = df['datetime'].max()

        key = str(username) + str(earliest_date) + str(latest_date)

        if (redis_manager.key_exists_boolean(key)):
            graph_data = redis_manager.get_value_by_key(key)
            return render_template('track.html', plot_url1=f'data:image/png;base64,{graph_data}', error=error)
        else:
            # Create a dictionary to store the data for each date
            dates = sorted(list(set(df['datetime'])))
            date_data = {date: {'food': [], 'transportation': [], 'household': [], 'expenses': [], 'total': []} for date in dates}

            graph_manager = graphCreator(df, dates, date_data)
            graph_data = graph_manager.create_tracking_graphs()
            redis_manager.set_key_value(key, graph_data)
    else:
        error = "No data available for this user"

    return render_template('track.html', plot_url1=f'data:image/png;base64,{graph_data}', error=error)

# Recommendations page
@app.route('/recommend')
def recommend_data():
    return render_template('recommend.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the 'username' key from the session
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
