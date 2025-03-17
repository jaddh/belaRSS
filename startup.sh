#!/bin/bash
# run_python.sh: Script to run a Python file on startup and start PNPM

# Change directory to your project folder so that relative paths work correctly.
cd /home/jaddh/belaRSS || exit

# Activate the virtual environment.
source /home/jaddh/belaRSS/.venv/bin/activate

# Run the Python script using the Python executable from the virtual environment.
# Using & to run it in the background so that the script continues.
python app.py &

# Optionally, you can capture the process ID if needed:
# PYTHON_PID=$!
# echo "Python app started with PID $PYTHON_PID"

# Change directory to the PNPM project folder.
cd RSSHub || exit

# Start the PNPM process.
pnpm start