

from flask import Flask, request, jsonify, send_file, session
import openai
import os
import psycopg2
from dotenv import load_dotenv
from datetime import date
import json

load_dotenv()


DATABASE_URL = 'postgres://brjyyccwesckpy:638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589@ec2-52-17-31-244.eu-west-1.compute.amazonaws.com:5432/dblua8qg5ehr18'
user_id = 11

def create_program():
    #update_chat_history(user_id=user_id, role='user', new_message= new_message)
    openai.api_key = os.getenv("OPENAI_API_KEY")

    #chat_history = get_chat_history(user_id=user_id)
    chat_history = []
    system_prompt = f"""
            You are a personal trainer. And are going to create a day by day custom running workout plan in 
            line with the user needs. The information that you want from the user is
            - are they training for a specific race? if they are, what date is the race and how long 
            is it? and do they have a certain goal time?
            - if they aren't training for a race, do they have any other running goals?
            - how many days a week do they have time to workout?
            - what is their current fitness like? for example are they beginners or advanced
            - have they ran any races before and in that case, what were their pbs?
            You can ask the user a few questions to get the information before creating the 
            workout plan. The workout plan should provide a schedule for all days up until the goal race and end with "RACE DAY!"
            or 3 months ahead in time. 
            Todays date is {date.today() }, All workouts should be in kilometers. 
            When you have presented the workout plan you should say "Does this sound good? If you want 
            to go ahed and add this plan
            to your schedule type yes"
            and if the user agrees to the plan you output only the detailed plan for every day in the following format:
            json object with key being the date “YYYY-MM-DD” and the value being a description 
            of the workout for that day.     
            """
            
    reminder = """remember that if the user agrees to the plan, you output only the workout plan in the following format:
            <SEPARATOR> [["date", "workout"], ["date", "workout"],....] <SEPARATOR> """
    system_msg = {"role" : "system", "content" : system_prompt}
    chat_history.append(system_msg)
    
    while(True):
        new_message = input("what do you want to say?")
        
        user_msg = {"role" : "user", "content" : new_message}

        chat_history.append(user_msg)

        model = "gpt-3.5-turbo-0613"
        response = openai.ChatCompletion.create(
            model=model,
            messages=chat_history,
            temperature=0,
        )

        response = response.choices[0].message["content"]
        chat_history.append({"role" : "assistant", "content" : response})
        
        print(response)
        if(new_message.lower() == "yes"):
            insert_into_database(user_id, response)
            break

def insert_into_database(user_id, workout_plan):
    
    json_format= workout_plan.split("{")[1]
    json_format = json_format.split("}")[0]
    json_format = "{"+ json_format+ "}"

    json_format = json.loads(json_format)


    DATABASE_URL = 'postgres://brjyyccwesckpy:638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589@ec2-52-17-31-244.eu-west-1.compute.amazonaws.com:5432/dblua8qg5ehr18'

    # create database connection
    for item in json_format:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        the_date = item
        workout = json_format[the_date]
        cur.execute(f"INSERT INTO workout_schedule (date, workout, user_id) VALUES ('{the_date}', '{workout}','{user_id}');")
        conn.commit()
    cur.close()
    conn.close() 

    
def get_workout_specific_date(date, user_id):
    
    DATABASE_URL = 'postgres://brjyyccwesckpy:638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589@ec2-52-17-31-244.eu-west-1.compute.amazonaws.com:5432/dblua8qg5ehr18'
    # create database connection
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(f"SELECT workout FROM workout_schedule WHERE date = '{date}' AND user_id = '{user_id}';")
    exists = cur.fetchall()
    if len(exists) == 0:
        print(" workout doesn't exist ")
        message = " user doesn't exist "
    
    elif len(exists) == 1:
        print(exists[0][0])
    
    cur.close()
    conn.close() 

    
    
    
    
    

        
    
    
    
    
if __name__ == '__main__':
    create_program()
    get_workout_specific_date("2023-12-16", 13)

def get_chat_history(user_id):
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

    # Check security on this query
    query = "SELECT * FROM user_chat_history WHERE user_id = %s ORDER BY message_id;"

    cursor.execute(query, (user_id, ))
    
    chat_history_object = cursor.fetchall()

    chat_history = []

    for message in chat_history_object:
        msg_object = {"role": message[2], "content": message[3]}
        chat_history.append(msg_object)

    cursor.close()
    conn.close()

    return chat_history


def update_chat_history(user_id, role, new_message):
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

    query = """INSERT INTO user_chat_history (user_id, role, content) VALUES (%s, %s, %s);"""

    cursor.execute(query, (user_id, role, new_message))

    conn.commit()

    cursor.close()
    conn.close()