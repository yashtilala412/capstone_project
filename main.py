import csv
import json
import os
from dotenv import load_dotenv
from flask import Flask
from groq import Groq
import sqlite3

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


def store_data(data_object,response,command):
    """
    Stores the provided data object into the llm_data table in the SQLite database.

    Args:
        data_object (dict): A dictionary containing the following keys:
            - error_name (str): Name of the error.
            - error_data (str): Detailed error information.
            - application_name (str): Name of the application.
            - llm_output (str): Output from the LLM.
            - commands (str): Commands suggested to resolve the error.
            - status (bool): Status of whether the error is resolved.
    """
    # Database file name
    db_file = "output.db"

    # Establish connection to the SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the table if it does not exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS llm_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        error_name TEXT NOT NULL,
        error_data TEXT NOT NULL,
        application_name TEXT NOT NULL,
        llm_output TEXT NOT NULL,
        commands TEXT NOT NULL,
        status BOOLEAN NOT NULL DEFAULT 0
    );
    """
    cursor.execute(create_table_query)

    # Insert data into the table
    insert_query = """
    INSERT INTO llm_data (error_name, error_data, application_name, llm_output, commands, status)
    VALUES (?, ?, ?, ?, ?, ?);
    """

    # Extract values from the data_object
    values = (
        data_object["error_name"],
        data_object["error_data"],
        data_object["application_name"],
        response,
        command,
        False,
    )

    # Execute the insert query
    cursor.execute(insert_query, values)

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()


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
        response=groq_model_call(user_prompt)
        store_data(json_object,response,response)

# Execute the process
# if __name__ == '__main__':
#     app.run(debug=True)
    # File path to the CSV
file_path = './error_table.csv'
process_csv(file_path)


