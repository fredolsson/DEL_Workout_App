from flask import Flask, request, jsonify
import openai
import os


app = Flask(__name__)

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
    app.run()

