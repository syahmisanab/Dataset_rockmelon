import cv2
import numpy as np
import tkinter as tk
from tkinter import Label, Frame
from PIL import Image, ImageTk, ImageGrab
from datetime import datetime
import serial
import threading
import sys
import time
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from utils import visualize  # Make sure this module is available

# Define serial port (adjust according to your setup)
SERIAL_PORT = '/dev/ttyUSB0'  # Replace with the correct serial port
BAUD_RATE = 9600

# Global variables for sensor data
fruit_temperature = "-"
fruit_gas = "-"
soil_temperature = "-"
soil_moisture = "-"
soil_ph = "-"

# Global variables to calculate FPS
COUNTER, FPS = 0, 0
START_TIME = time.time()
detection_frame = None  # Initialize detection_frame
detection_result_list = []

# Function to receive data from Arduino
def receive_data():
    global fruit_temperature, fruit_gas, soil_temperature, soil_moisture, soil_ph
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').rstrip()
            print(f"Received data: {data}")
            parse_data(data)

# Function to parse received data
def parse_data(data):
    global fruit_temperature, fruit_gas, soil_temperature, soil_moisture, soil_ph
    try:
        if data.startswith("ObjectTemp:"):
            fruit_temperature = data.split(':')[1]
    except Exception as e:
        print(f"Error parsing data: {e}")

# Function to save data (screenshot)
def save_data():
    # Capture the current state of the UI
    window.update_idletasks()  # Ensure all pending events are processed
    x, y, w, h = window.winfo_rootx(), window.winfo_rooty(), window.winfo_width(), window.winfo_height()
    screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))  # Capture the window screenshot
    
    # Get the filename from the entry box
    filename = filename_entry.get().strip()
    
    # If the filename is empty, use a default name
    if not filename:
        filename = "screenshot"
    
    # Clear the entry box
    filename_entry.delete(0, tk.END)
    
    screenshot_path = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    screenshot.save(screenshot_path)
    print(f"Saved combined screenshot to {screenshot_path}")

# Function to update frames with MediaPipe object detection
def update_frame():
    global COUNTER, FPS, START_TIME, detection_frame

    success, image = cap.read()
    if not success:
        sys.exit('ERROR: Unable to read from webcam. Please verify your webcam settings.')

    image = cv2.flip(image, 1)

    # Convert the image from BGR to RGB as required by the TFLite model.
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    # Run object detection using the model.
    detector.detect_async(mp_image, time.time_ns() // 1_000_000)

    # Show the FPS
    if COUNTER % fps_avg_frame_count == 0:
        FPS = fps_avg_frame_count / (time.time() - START_TIME)
        START_TIME = time.time()

    fps_text = 'FPS = {:.1f}'.format(FPS)
    text_location = (left_margin, row_size)
    current_frame = image
    cv2.putText(current_frame, fps_text, text_location, cv2.FONT_HERSHEY_DUPLEX,
                font_size, text_color, font_thickness, cv2.LINE_AA)

    if detection_result_list:
        current_frame = visualize(current_frame, detection_result_list[0])
        detection_frame = current_frame
        detection_result_list.clear()

    if detection_frame is not None:
        img1 = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(detection_frame, cv2.COLOR_BGR2RGB)))
        label1.config(image=img1)
        label1.image = img1

    # Update sensor data labels
    label_fruit_temp.config(text=f"(fruit) Temperature: {fruit_temperature} °C")
    label_fruit_gas.config(text=f"(fruit) Gas Ethylene: {fruit_gas} ppm")
    label_soil_temp.config(text=f"(soil) Temperature: {soil_temperature} °C")
    label_soil_moisture.config(text=f"(soil) Moisture: {soil_moisture} %")
    label_soil_ph.config(text=f"(soil) pH: {soil_ph}")

    window.after(10, update_frame)

# Function to update the time label
def update_time():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_label.config(text=current_time)
    window.after(1000, update_time)  # Update every second

# Initialize serial communication
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Serial port {SERIAL_PORT} opened successfully.")
except serial.SerialException as e:
    print(f"Failed to open serial port {SERIAL_PORT}: {e}")
    exit()

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Set camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize the object detection model
model = 'model.tflite'
max_results = 5
score_threshold = 0.5
fps_avg_frame_count = 10
row_size = 50  # pixels
left_margin = 24  # pixels
text_color = (0, 0, 0)  # black
font_size = 1
font_thickness = 1

def save_result(result: vision.ObjectDetectorResult, unused_output_image: mp.Image, timestamp_ms: int):
    global FPS, COUNTER, START_TIME

    # Calculate the FPS
    if COUNTER % fps_avg_frame_count == 0:
        FPS = fps_avg_frame_count / (time.time() - START_TIME)
        START_TIME = time.time()

    detection_result_list.append(result)
    COUNTER += 1

base_options = python.BaseOptions(model_asset_path=model)
options = vision.ObjectDetectorOptions(base_options=base_options,
                                       running_mode=vision.RunningMode.LIVE_STREAM,
                                       max_results=max_results, score_threshold=score_threshold,
                                       result_callback=save_result)
detector = vision.ObjectDetector.create_from_options(options)

# Create a window
window = tk.Tk()
window.title("Object Detection with Sensor Data")

# Create a frame for the object detection
frame_detection = Frame(window, width=640, height=480, bd=2, relief=tk.SOLID)
frame_detection.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

# Create labels to show the images
label1 = Label(frame_detection)
label1.pack()

# Create a frame for the buttons, text entry, and sensor data
frame_controls = Frame(window, width=640, height=200, bd=2, relief=tk.SOLID)
frame_controls.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# Create time label
time_label = Label(frame_controls, text="", width=20)
time_label.grid(row=0, column=0, columnspan=2, pady=5)

# Create text entry for the filename
filename_entry = tk.Entry(frame_controls, width=20)
filename_entry.grid(row=1, column=0, columnspan=2, pady=5)

# Create buttons
button_save = tk.Button(frame_controls, text="Save Data", command=save_data, width=20, height=2)
button_save.grid(row=2, column=0, pady=5)

button_refresh = tk.Button(frame_controls, text="Refresh", width=20, height=2)
button_refresh.grid(row=2, column=1, pady=5)

# Create a frame for the sensor data
frame_sensors = Frame(window, width=640, height=240, bd=2, relief=tk.SOLID)
frame_sensors.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Create labels for sensor data
label_fruit_temp = Label(frame_sensors, text=f"(fruit) Temperature: {fruit_temperature} °C", width=75)
label_fruit_temp.pack(anchor='center', padx=10, pady=5)

label_fruit_gas = Label(frame_sensors, text=f"(fruit) Gas Ethylene: {fruit_gas} ppm", width=75)
label_fruit_gas.pack(anchor='center', padx=10, pady=5)

label_soil_temp = Label(frame_sensors, text=f"(soil) Temperature: {soil_temperature} °C", width=75)
label_soil_temp.pack(anchor='center', padx=10, pady=5)

label_soil_moisture = Label(frame_sensors, text=f"(soil) Moisture: {soil_moisture} %", width=75)
label_soil_moisture.pack(anchor='center', padx=10, pady=5)

label_soil_ph = Label(frame_sensors, text=f"(soil) pH: {soil_ph}", width=75)
label_soil_ph.pack(anchor='center', padx=10, pady=5)

# Start thread to receive data from Arduino
data_thread = threading.Thread(target=receive_data)
data_thread.start()

# Start updating frames
update_frame()

# Start updating the time
update_time()

# Start the Tkinter main loop
window.mainloop()

# Release the camera when done
cap.release()
cv2.destroyAllWindows()
