import io
from flask import Flask, request, jsonify, send_file, session
from flask_session import Session
import os
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from pandas import DataFrame as df
#from dotenv import load_dotenv
from datetime import date
from help_methods import *
from variables_and_prompts import *


app = Flask(__name__)


#app.secret_key = os.getenv("APP_SECRET_KEY")

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
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    # Get the user's query from the request

    user_id = get_user_id(request.json.get('username'))

    update_chat_history(user_id=user_id, role='user', new_message=request.json.get('query'))
    
    chat_history = get_chat_history(user_id=user_id)

    system_prompt = """
        You are a personal trainer. You will do your best to answer each question
        with a tone that imitates how a personal trainer would answer it.
        You will answer each question with a maximum of five sentences. Note that 
        you do not need to use 3 sentences if you do not need it. You will start 
        each message with 'Hello there young running padawan!', and then answer the question.
        """

    system_msg = {"role" : "system", "content" : system_prompt}

    chat_history.append(system_msg)

    model = "gpt-3.5-turbo-0613"
    response = openai.ChatCompletion.create(
        model=model,
        messages=chat_history,
        temperature=0.9,
    )

    response = response.choices[0].message["content"]

    update_chat_history(user_id=user_id, role='assistant', new_message=response)

    # Return the response in JSON format
    return jsonify({"response": response})


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
    
@app.route('/api/get_workout', methods=['POST'])
def get_workout_specific_date():
    date = request.json.get('date')

    try:
        user_id = get_user_id(request.json.get('username'))
        exists = execute("SELECT workout FROM workout_schedule WHERE date = %s AND user_id = '%s';", [date, user_id],commit = False)
        if len(exists) == 0:
            message = "Rest Day"
        
        else:
            message = exists[0][0]
    except Exception as error:
        print("Error while connecting to PostgreSQL:", error)
        message = "username doesn't exist"
            
    return jsonify({"response": message}) 

@app.route('/api/create_workout', methods=['POST'])
def create_workout():
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        user_id = get_user_id(request.json.get('username'))
        exists = execute("SELECT role, content FROM generation_chat_history WHERE user_id = %s;",[user_id], commit=False)
        if len(exists) == 0:
            execute("INSERT INTO generation_chat_history (user_id, role, content) VALUES (%s, 'system', %s);", [user_id, prompt_create_scedule], commit=True)
            print("inserted prompt")
        execute("INSERT INTO generation_chat_history (user_id, role, content) VALUES (%s, 'user', %s);", [user_id, request.json.get('content')], commit=True)
        chat_history_object = execute("SELECT * FROM generation_chat_history WHERE user_id = %s ORDER BY id;", [user_id], commit=False)
        chat_history = []
        for message in chat_history_object:
            msg_object = {"role": message[3], "content": message[2]}
            chat_history.append(msg_object)

        model = "gpt-3.5-turbo-0613"

        response = openai.ChatCompletion.create(
            model=model,
            messages=chat_history,
            temperature=0,
        )
        response = response.choices[0].message["content"]
        execute("INSERT INTO generation_chat_history (user_id, role, content) VALUES (%s, 'assistant', %s);", [user_id, response], commit = True)
        message = response

        
        if request.json.get('content').lower() == "yes":
            print("deleting")
            delete_workout_for_user(user_id)
            print("deleted")
            print("inserting new workout")
            insert_into_database(user_id, response)
            print("inserted")
            print("saving goals")
            chat_history.pop(0)
            set_goals(chat_history, user_id) # skicka allt förutom prompt
            print("information inserted")
            delete_create_history(user_id)
            print("deleted")
            message = "done"
            
    except Exception as error:
        print(f"error {error}")
        message = "fail"
    
    return jsonify({"response": message})
    
@app.route('/api/get_goal', methods=['POST'])
def get_goal():
    user_id = get_user_id(request.json.get('username'))
    data = execute("SELECT goal FROM user_information WHERE user_id = %s", [user_id], commit=False)
    if len(data) == 0:
        message = "No goal"
        
    else:
        message = data[0][0]
    
    return jsonify({"response": message})
    

if __name__ == '__main__':
    app.run()