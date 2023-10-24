
import io
from flask import Flask, request, jsonify, send_file, session
import openai
import os
import bcrypt
from sqlalchemy import create_engine
from pandas import DataFrame as df
import psycopg2
import json

workout_plan = """{
  "23-10-23": "6 km easy run",
  "25-10-23": "8 km moderate pace",
  "27-10-23": "10 km long run",
  "30-10-23": "6 km easy run",
  "01-11-23": "8 km moderate pace",
  "03-11-23": "10 km long run",
  "06-11-23": "6 km easy run",
  "08-11-23": "8 km moderate pace",
  "10-11-23": "12 km long run",
  "13-11-23": "6 km easy run",
  "15-11-23": "8 km moderate pace",
  "17-11-23": "12 km long run",
  "20-11-23": "6 km easy run",
  "22-11-23": "10 km moderate pace",
  "24-11-23": "14 km long run",
  "27-11-23": "6 km easy run",
  "29-11-23": "10 km moderate pace",
  "01-12-23": "14 km long run",
  "04-12-23": "8 km easy run",
  "06-12-23": "10 km moderate pace",
  "08-12-23": "14 km long run",
  "11-12-23": "8 km easy run",
  "13-12-23": "10 km moderate pace",
  "15-12-23": "14 km long run",
  "18-12-23": "8 km easy run",
  "20-12-23": "10 km moderate pace",
  "22-12-23": "14 km long run",
  "25-12-23": "8 km easy run",
  "27-12-23": "10 km moderate pace",
  "29-12-23": "14 km long run",
  "01-01-24": "8 km easy run",
  "03-01-24": "10 km moderate pace",
  "05-01-24": "8 km easy run",
  "07-01-24": "MARATHON RACE DAY!"
} good louch with it"""

DATABASE_URL = 'postgres://brjyyccwesckpy:638b0040bc3765bf41a90f060604f05e2130fd1daf9382bf72dfa3dd4807f589@ec2-52-17-31-244.eu-west-1.compute.amazonaws.com:5432/dblua8qg5ehr18'
# json_format= workout_plan.split("{")[1]
# json_format = json_format.split("}")[0]
# json_format = "{"+ json_format+ "}"
# json_format = json.loads(json_format)
# print(json_format)
# # cre
# # ate database connection
# for item in json_format:
#     print(item)
#     print(json_format[item])
# #         conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# #         cur = conn.cursor()
# #         the_date = 
# #         cur.execute(f"INSERT INTO workout_schedule(id, date, workout) VALUES ({user_id}, {the_date}, {workout});")
# #         conn.commit()
# #         cur.close()
# #         conn.close() 
    
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
cur.execute("ALTER TABLE workout_schedule ADD user_id int;")
conn.commit()
cur.close()
conn.close()