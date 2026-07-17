import os
import sys

# Dynamically add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.app import App

if __name__ == "__main__":
    app = App()
    app.run()


