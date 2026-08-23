Gesture-Based Media & System Controller

A real-time Python desktop application that transforms hand gestures into system media and audio controls. Built with MediaPipe Tasks API, OpenCV, and a dark-themed CustomTkinter GUI, this application processes video feeds in a background thread to maintain high responsiveness.

Key Features

Dynamic Volume Control: Pinch your thumb and index finger together to adjust system volume smoothly.

Next/Previous Track: Raise your Right Hand to jump to the next song, or your Left Hand for the previous song.

Fast Forward & Rewind: Point your index finger and tilt it right to seek forward or left to rewind.

High-Five Quick Lock: Show an open palm (all 5 fingers raised) to instantly trigger a borderless, full-screen black screen overlay for instant privacy.

Multithreaded GUI: Camera streaming and hand landmark detection run asynchronously, ensuring zero UI lag.

Tech Stack & Requirements

Language: Python 3.9+

Computer Vision: OpenCV, MediaPipe (Tasks API)

Audio & System Controls: PyCaw, Keyboard Module

Graphical Interface: CustomTkinter, Pillow (PIL)

Installation & Setup

Clone the Repository
git clone https://github.com/faizitech11/Gesture-recognition/
cd YOUR_REPOSITORY_NAME

Install Dependencies
pip install opencv-python mediapipe pycaw customtkinter pillow keyboard

Download the MediaPipe Model
Ensure the MediaPipe Hand Landmarker model file is present in your project directory:
Download hand_landmarker.task from the official MediaPipe developer site and save it as hand_landmarker.task in the root folder.

Run the Application
python hot.py

Gesture Reference Guide

Thumb & Index Pinch -> Adjust System Volume
Right Hand Raised -> Next Track
Left Hand Raised -> Previous Track
Index Finger Tilt Right -> Fast Forward
Index Finger Tilt Left -> Rewind
Open Palm (High-Five) -> Fullscreen Black Lock Screen

Controls & Dismissal

To dismiss the High-Five Black Screen, press ESC or click anywhere on the screen.# Gesture-recognition
A modern Python-based computer vision application that leverages MediaPipe and OpenCV to control system volume, skip tracks, seek media, and trigger a privacy screen using intuitive hand gestures.
