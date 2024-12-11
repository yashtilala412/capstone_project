import subprocess
import time
import os
import logging
import sys

# Initialize logging
logging.basicConfig(filename='app_monitor.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def clone_repo(git_url, clone_path):
    """Clone the given Git repository."""
    logging.info(f"Cloning repository from {git_url} to {clone_path}")
    try:
        subprocess.run(["git", "clone", git_url, clone_path], check=True)
        logging.info("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clone repository: {e}")
        sys.exit(1)


def detect_project_type(clone_path):
    """Detect the project type based on files in the cloned repository."""
    if os.path.exists(os.path.join(clone_path, 'package.json')):
        return 'react'
    elif os.path.exists(os.path.join(clone_path, 'pom.xml')):
        return 'java'
    elif os.path.exists(os.path.join(clone_path, 'composer.json')):
        return 'php'
    elif os.path.exists(os.path.join(clone_path, 'index.html')):
        return 'html'
    else:
        return 'unknown'


def install_dependencies(project_type, clone_path):
    """Install dependencies for the detected project type."""
    logging.info(f"Installing dependencies for {project_type} project.")
    try:
        if project_type == 'react':
            npm_path = r"C:\Program Files\nodejs\npm.cmd" 
            if not os.path.exists(npm_path):
                raise FileNotFoundError("npm not found. Please ensure Node.js is installed and npm is in your PATH.")
            subprocess.run([npm_path, "install"], cwd=clone_path, check=True)
            # subprocess.run(["npm", "install"], cwd=clone_path, check=True)
        elif project_type == 'java':
            subprocess.run(["mvn", "install"], cwd=clone_path, check=True)
        elif project_type == 'php':
            subprocess.run(["composer", "install"], cwd=clone_path, check=True)
        else:
            logging.warning(f"No dependency installation required for {project_type}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install dependencies: {e}")
        sys.exit(1)


def run_application(project_type, clone_path):
    """Run the application based on its type."""
    logging.info(f"Running {project_type} application.")
    try:
        if project_type == 'react':
            command = ["npm", "start"]
        elif project_type == 'java':
            command = ["mvn", "spring-boot:run"]
        elif project_type == 'php':
            command = ["php", "-S", "localhost:8000"]
        elif project_type == 'html':
            logging.info("Open index.html in a browser for static HTML applications.")
            return None
        else:
            logging.error("Unsupported project type.")
            return None

        process = subprocess.Popen(command, cwd=clone_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return process
    except Exception as e:
        logging.error(f"Failed to run application: {e}")
        sys.exit(1)


def monitor_application(process):
    """Monitor the application process and capture its output."""
    try:
        while True:
            output = process.stdout.readline()
            if output:
                logging.info(f"App output: {output.strip()}")

            error = process.stderr.readline()
            if error:
                logging.error(f"App error: {error.strip()}")

            # Check if process has terminated
            retcode = process.poll()
            if retcode is not None:
                # Process has terminated
                logging.info(f"Application terminated with exit code {retcode}")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Monitoring interrupted.")
        process.terminate()
        logging.info("Application stopped manually.")


if __name__ == "__main__":
    git_url = input("Enter the Git repository URL: ")
    clone_path = os.path.join(os.getcwd(), "cloned_repo")

    # Step 1: Clone the repository
    clone_repo(git_url, clone_path)

    # Step 2: Detect the project type
    project_type = detect_project_type(clone_path)
    logging.info(f"Detected project type: {project_type}")

    # Step 3: Install dependencies (if necessary)
    install_dependencies(project_type, clone_path)

    # Step 4: Run the application
    process = run_application(project_type, clone_path)

    if process:
        # Step 5: Monitor the application
        monitor_application(process)
