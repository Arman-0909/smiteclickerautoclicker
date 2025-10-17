Advanced Autoclicker with Fluent UI
A powerful, feature-rich autoclicker built with Python and PyQt6. This application goes beyond simple clicking, offering advanced targeting controls, multiple activation modes, and a sleek, modern user interface inspired by Fluent Design.
It is designed to be both highly functional for complex tasks and easy to use for simple automation.
Features
This autoclicker is packed with features that provide precision, control, and convenience.
Clicking Options
Adjustable Click Speed: Set a precise number of clicks per second (CPS).
CPS Modes: Choose from pre-configured speed tiers (Normal, Fast, Extreme, Insane), which come with warnings for high-risk speeds.
Click Type: Emulate single or double-clicks.
Mouse Button: Select left, right, or middle mouse buttons for clicking.
Click Randomization: Introduce slight, random delays between clicks to mimic human behavior and avoid detection.
Click Limiter: Automatically stop the autoclicker after a specific number of clicks has been reached.
Advanced Targeting Control
Current Mouse Position: Clicks at the current location of your mouse cursor.
Specific Coordinates: Set a fixed X/Y coordinate on the screen for all clicks.
Pixel-Perfect Location Picker: An overlay tool with a magnifier to precisely select screen coordinates.
Specific Window Targeting: A powerful filter that restricts all clicking actions to a chosen application window. The autoclicker will automatically pause if the mouse moves outside the window and resume when it re-enters.
Activation & Hotkeys
Customizable Hotkeys: Set your own keys to start and stop the autoclicker.
Dual Activation Modes:
Toggle Mode: Press the start key to begin clicking and the stop key to end.
Hold Mode: Clicking is only active while the activation hotkey is being held down.
Profiles & Sessions
Profile System: Save and load different configurations for various tasks.
Session Logs: View a history of past autoclicking sessions.
Modern User Interface
Fluent Design: A clean, professional dark theme with custom-styled widgets.
Animated Transitions: Smooth fade and slide animations when switching between views.
Installation
To run this application, you will need Python 3 and a few external libraries.
1. Requirements
Python 3.x
2. Setup
Clone the repository to your local machine:
code
Bash
git clone <your-repository-url>
Navigate into the project directory:
code
Bash
cd autoclicker
Install the required Python libraries. It's recommended to do this in a virtual environment.
code
Bash
pip install PyQt6 pynput pygetwindow
Run the application:
code
Bash
python main.py
How to Use
The application is organized into several views accessible from the sidebar.
Dashboard: This is the main screen where you can quickly start/stop the autoclicker and configure the most common settings like CPS, mouse button, and click type.
Click Targeting: Configure where the clicks should happen. Choose between your current mouse position, a fixed coordinate, or filter all clicks to a specific window.
Profiles: Save your current settings as a new profile or load an existing one.
Session Logs: See a table of your past sessions.
Settings: Configure the application's global settings, such as the start/stop hotkeys and the activation mode (Toggle vs. Hold).
