"""
main.py
-------
Entry point for the AI Chatbot application.
Run this file to start the chatbot:

    python main.py

All logic lives in the modules below — this file stays intentionally thin.
"""

import sys
import os

# Ensure the project root is on the Python path so all imports work
# regardless of how/where python main.py is called from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.interface import run


if __name__ == "__main__":
    run()
