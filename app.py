import io
from flask import Flask, request, jsonify, send_file, session
from flask_session import Session
import openai
import os
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from pandas import DataFrame as df
import psycopg2

DATABASE_URL = 'postgres://brjyyccwesckpy:638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589@ec2-52-17-31-244.eu-west-1.compute.amazonaws.com:5432/dblua8qg5ehr18'

app = Flask(__name__)

app.secret_key = os.getenv("APP_SECRET_KEY")

@app.route('/api/register', methods=['POST'])
def register():
    # test connection
    try:
        username = request.json.get('username')

        # create database connection
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute("SELECT id FROM credentials WHERE username=%s;", [username])

        exists = cur.fetchall()
        if len(exists) != 0:
            print("usernme alredy in use ")   
            message = "usernme alredy in use "
            
        
        else:
            password = request.json.get('password')
            password = password.encode('utf-8')
            hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
            cur.execute("INSERT INTO credentials (username, password) VALUES(%s, %s);", (username, hashed))
            conn.commit()
            print("successfully registered")
            cur.execute("SELECT * FROM credentials;")
            print(cur.fetchall())

            message = "successfully registered"
            
        cur.close()
        conn.close()
        return jsonify({"message": message})

    except Exception as error:
        print('Cause:{}'.format(error)) 
        return jsonify({"message": "error"}) 
    

@app.route('/api/login', methods=['POST'])
def login():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        username = request.json.get('username')

        cur.execute("SELECT id FROM credentials WHERE username=%s;", [username])

        exists = cur.fetchall()
        print(exists)
        if len(exists) == 0:
            print(" user doesn't exist ")
            message = " user doesn't exist "
        
        elif len(exists) == 1:
            
            cur.execute("SELECT password FROM credentials WHERE id=%s;", [exists[0][0]])  
            stored_password = cur.fetchone()
            password = request.json.get('password')
            if bcrypt.checkpw(password.encode('utf-8'), stored_password[0].encode('utf-8')):
                print("successfully logged in")
                message = "successfully logged in"
            else:
                print("wrong password")
                message = "wrong password"
        else:
            print(" there are more than one user with this username")
            message = "there are more than one user with this username"
            
        cur.close()
        conn.close()
        return jsonify({"message": message}) 

        
    except Exception as error:
        print('Cause:{}'.format(error))  
        return jsonify({"message": "error"}) 

        



# This API can be called to receive a response from GPT. 
@app.route('/api/chatbot/response', methods=['POST'])
def chatbot():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # Get the user's query from the request
    user_query = request.json.get('query')

    user_msg = {"role" : "user", "content" : user_query+". You response needs to be maximum five sentences."}
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