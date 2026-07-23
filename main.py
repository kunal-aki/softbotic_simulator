import sys
import os

# Add the current directory to Python's module search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.app import SimulationApp

def main():
    app = SimulationApp(
        width=1280, 
        height=720, 
        title="BioSim 3D - Soft Robotics Assembly Grid"
    )
    app.run()

if __name__ == "__main__":
    main()


