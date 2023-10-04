from flask import Flask, request, jsonify
import openai
import os
import bcrypt


from sqlalchemy import create_engine
from pandas import DataFrame as df

import psycopg2

DATABASE_URL = 'postgres://brjyyccwesckpy:638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589@ec2-52-17-31-244.eu-west-1.compute.amazonaws.com:5432/dblua8qg5ehr18'

app = Flask(__name__)

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

        

# This API is just a test
@app.route('/api/data', methods=['GET'])
def get_data():
    
    data = {"message": "Hello from Flask!"}
    return jsonify(data)

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


if __name__ == '__main__':
    app.run(debug =True, port=9090)

