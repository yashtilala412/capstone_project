import subprocess

def run_command_in_prompt():
    print("Custom Command Prompt Interface (type 'exit' to quit)")
    
    while True:
        # Get the user input (command)
        command = input("Enter command: ")

        # Exit condition
        if command.lower() == "exit":
            print("Exiting custom command prompt.")
            break

        try:
            # Execute the command and capture the output and errors
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            # Display the command's standard output
            if result.stdout:
                print("Output:\n", result.stdout)
            
            # Display any errors
            if result.stderr:
                print("Error:\n", result.stderr)
        
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_command_in_prompt()
