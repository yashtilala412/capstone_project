import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Initialize the Groq client with the API key
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Route for the home page where users can input a question
@app.route('/')
def home():
    return '''
    <form method="POST" action="/ask">
        <label for="question">Ask a question:</label><br>
        <input type="text" id="question" name="question"><br>
        <input type="submit" value="Ask">
    </form>
    '''

# Route to handle the question input and call the model
@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form.get('question')

    if not question:
        return "No question provided!", 400

    # Call the Groq model with the user's question
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="llama3-8b-8192",
        )
        # Extract the response from the model
        response = chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}", 500

    # Return the model's response
    return f"<p><strong>Question:</strong> {question}</p><p><strong>Response:</strong> {response}</p>"

if __name__ == '__main__':
    app.run(debug=True)
