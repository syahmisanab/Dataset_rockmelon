# Rockmelon Monitoring System (Broken Code)

## **Overview**
This repository contains a **broken** implementation of a Rockmelon Monitoring System that integrates **Python**, **Arduino**, and **MediaPipe AI models** for real-time fruit and soil condition monitoring. The code was part of a project developed in 2023 but is no longer functional.

## **Functionality**
The system was intended to:
- **Capture live video** using OpenCV and detect objects (rockmelons) using **MediaPipe’s object detection model**.
- **Receive real-time sensor data** from an Arduino, including:
  - Fruit temperature
  - Ethylene gas levels (ripeness indicator)
  - Soil temperature, moisture, and pH
- **Display results in a GUI** (Tkinter) with live detection and sensor updates.
- **Save screenshots of the detection results** for logging and analysis.

## **Code Structure**
### **Python Code** (Detection & GUI)
- Uses OpenCV to access a webcam.
- Processes images with **MediaPipe’s TensorFlow Lite object detector**.
- Reads serial data from an Arduino (sensor readings).
- Displays a graphical user interface (Tkinter) with:
  - Live object detection view.
  - Sensor data values.
  - Buttons for saving results.
- Implements a **multithreaded serial reader** to handle Arduino communication without freezing the UI.

### **Arduino Code** (Sensor Data Collection)
- Reads temperature, humidity, electrical conductivity (EC), and pH from sensors.
- Uses **Modbus communication protocol** to interact with the sensors.
- Sends formatted sensor data via **serial communication** to the Python script.
- Implements **CRC16 error checking** to ensure data integrity.

## **Object Detection Model**
The model used for object detection was trained following Google AI Edge’s **MediaPipe customization tutorial**:
👉 [Custom Object Detector with MediaPipe](https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/customization/object_detector.ipynb)

## **Annotation Tool**
To label training images, **LabelImg** was used:  
🔗 [LabelImg GitHub](https://github.com/heartexlabs/labelImg)

## **Status**
🚨 **This code is broken and does not function properly.** 🚨  
- The **serial communication has issues** (may fail to read data properly).
- The **MediaPipe object detection may not work** due to incorrect model loading.
- The **GUI may freeze** due to blocking operations.

This repository serves as a reference for the past project, but it is **not usable in its current state** without significant debugging and fixes.

---

## **Notes**
- this code was scrapped from interaction from chatgpt for debugging. the full working code was on the raspberry pi that is send to the client. i kinda regret not make a copy for it but its is what its is.  

