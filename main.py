import csv
import json
import os
from dotenv import load_dotenv
from flask import Flask
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
def make_prompt(json_object):
    """
    Creates a prompt for the GROQ model based on the error details from a JSON object.
    """
    # Parse the JSON object to extract fields
    application_name = json_object.get('application_name', 'Unknown Application')
    error_name = json_object.get('error_name', 'Unknown Error')
    error_data = json_object.get('error_data', 'No additional details provided.')
    
    # Construct the prompt and store it in the user_prompt variable
    user_prompt = (
        f"The application '{application_name}' encountered an error:\n\n"
        f"Error Name: {error_name}\n"
        f"Error Details: {error_data}\n\n"
        f"Please analyze this error and provide the commands by running that command  i can solve the error ."
    )
    
    # Return the prompt
    return user_prompt

def groq_model_call(prompt):
    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role":"system",
                    "content":"In the application there is error give me the best suitable solution for the error."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        # Extract the response from the model
    response = chat_completion.choices[0].message.content
    print(response)
    return response
def read_csv(file_path):
    """
    Reads the CSV file and returns a list of rows.
    """
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader]
    return rows

def convert_row_to_json(row):
    """
    Converts a CSV row (dictionary) into a JSON object.
    """
    return json.dumps(row, indent=4)

def process_csv(file_path):
    """
    Processes the CSV file row by row, converts each to JSON, and prints it.
    """
    rows = read_csv(file_path)
    for row in rows:
        json_string = convert_row_to_json(row)
        json_object = json.loads(json_string)
        user_prompt=make_prompt(json_object)
        print(json_object)
        groq_model_call(user_prompt)

# Execute the process
# if __name__ == '__main__':
#     app.run(debug=True)
    # File path to the CSV
file_path = './error_table.csv'
process_csv(file_path)


