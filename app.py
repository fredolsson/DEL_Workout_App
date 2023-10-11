import io
from flask import Flask, request, jsonify, send_file, session
from flask_session import Session

import openai
import os
import psycopg2

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.secret_key = os.getenv("APP_SECRET_KEY")
app.secret_key = "very_secret_key"

# This API can be called to receive a response from GPT. 
@app.route('/api/chatbot/response', methods=['POST'])
def chatbot():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # Get the user's query from the request
    user_query = request.json.get('query')

    user_msg = {"role" : "user", "content" : user_query}
    messages = [user_msg]

    model = "gpt-3.5-turbo-0613"
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.9,
    )

    response = response.choices[0].message["content"]

    # Return the response in JSON format
    return jsonify({"response": response})
# FIX: Get the username from session['username'] instead
@app.route('/api/get_profile_pic')
def send_profile_pic():

    user_id = str(get_user_id())
    
    try:
        conn = psycopg2.connect(
            dbname="dblua8qg5ehr18",
            user="brjyyccwesckpy",
            password="638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589",
            host="ec2-52-17-31-244.eu-west-1.compute.amazonaws.com",
            port="5432"
        )
        cursor = conn.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
    
    try:
        select_query = "SELECT profile_pic FROM user_profiles WHERE user_id = %s;"
        cursor.execute(select_query, (user_id,))
        profile_pic_data = cursor.fetchone()[0]

    except (Exception, psycopg2.Error) as error:
        conn.rollback()
        print("Error inserting row:", error)

    finally:
        cursor.close()
        conn.close()
    
    image_stream = io.BytesIO(profile_pic_data)

    return send_file(
        image_stream,
        mimetype='image/png'  
    )

@app.route('/api/set_profile_pic', methods=['POST'])
def set_profile_pic(profile_pic):

    username = session

    try:
        conn = psycopg2.connect(
            dbname="dblua8qg5ehr18",
            user="brjyyccwesckpy",
            password="638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589",
            host="ec2-52-17-31-244.eu-west-1.compute.amazonaws.com",
            port="5432"
        )
        cursor = conn.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
    
    try:
        with open(profile_pic, "rb") as image_file:
            profile_pic = image_file.read()  # Read the image as binary data

        insert_query = "INSERT INTO user_profiles (username, profile_pic) VALUES (%s, %s);"
        cursor.execute(insert_query, (username, profile_pic))

        conn.commit()
        print("Row inserted successfully.")

    except (Exception, psycopg2.Error) as error:
        conn.rollback()
        print("Error inserting row:", error)
    finally:
        cursor.close()
        conn.close()
    
@app.route('/api/get_profile_info')
def send_profile_info():
    followers_count = 100
    following_count = 50

    profile_data = {
        'Followers': followers_count,
        'Following': following_count
    }

    return jsonify(profile_data)

@app.route('/api/set_session/<username>')
def set_session(username):
    session['username'] = username
    return f"Session created for user: {username}"

@app.route('/api/test_session')
def test_session():
    
    send_profile_pic()

def get_user_id():

    username = session['username']

    try:
        conn = psycopg2.connect(
            dbname="dblua8qg5ehr18",
            user="brjyyccwesckpy",
            password="638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589",
            host="ec2-52-17-31-244.eu-west-1.compute.amazonaws.com",
            port="5432"
        )
        cursor = conn.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
    
    try:
        select_query = "SELECT id FROM credentials WHERE username = %s;"
        cursor.execute(select_query, (username,))
        user_id = cursor.fetchone()[0]

    except (Exception, psycopg2.Error) as error:
        conn.rollback()
        print("Error inserting row:", error)

    return user_id

if __name__ == '__main__':
    app.run()