import sqlite3
import json

def initialize_database(db_name="prompts.db"):
    """
    Initialize the SQLite database with a 'prompts' table.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        ALTER TABLE prompts
        ADD COLUMN error TEXT;
    ''')

    cursor.execute('''
        ALTER TABLE prompts
        ADD COLUMN pod TEXT;
    ''')

    cursor.execute('''
        ALTER TABLE prompts
        ADD COLUMN namespace TEXT;
    ''')

    cursor.execute('''
        ALTER TABLE prompts
        ADD COLUMN container TEXT;
    ''')

    cursor.execute('''
        ALTER TABLE prompts
        ADD COLUMN log TEXT;
    ''')

    cursor.execute('''
        ALTER TABLE prompts
        ADD COLUMN info TEXT;
    ''')

    conn.commit()
    conn.close()

def insert_prompt(key, value, db_name="prompts.db"):
    """
    Insert a new prompt into the database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO prompts (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_prompt(query, db_name="prompts.db"):
    """
    Retrieve a prompt based on the provided JSON object or text message.
    :param query: JSON object or text message as a string.
    :param db_name: SQLite database file name.
    :return: Matching prompt or a default message if no match is found.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Convert the query to JSON if it's a JSON string
    try:
        query_dict = json.loads(query)
        query_keys = list(query_dict.keys())
    except json.JSONDecodeError:
        query_keys = [query]  # Treat query as a text message if not JSON

    # Search for a matching key in the database
    for key in query_keys:
        cursor.execute('SELECT value FROM prompts WHERE key = ?', (key,))
        result = cursor.fetchone()
        if result:
            conn.close()
            return result[0]

    conn.close()
    return "No matching prompt found."

# Example Usage
if __name__ == "__main__":
    # Initialize and populate database
    initialize_database()
    insert_prompt("greeting", "Hello! How can I assist you today?")
    insert_prompt("farewell", "Goodbye! Have a great day!")
    
    # Query using text
    print(get_prompt("greeting"))  # Output: Hello! How can I assist you today?

    # Query using JSON
    example_json = json.dumps({"greeting": "Hi"})
    print(get_prompt(example_json))  # Output: Hello! How can I assist you today?

    # Query with no match
    print(get_prompt("unknown"))  # Output: No matching prompt found.
