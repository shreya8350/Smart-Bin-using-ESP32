# Smart Bin Using ESP32

An IoT-based Smart Waste Management System built using ESP32, ultrasonic sensors, GPS, and Python. The system monitors waste levels, automatically controls the bin lid, detects when the bin is full, and provides real-time monitoring through a desktop application.

## Project Overview

The Smart Bin System is designed to improve waste management through automated waste-level monitoring and location tracking.

It uses an ESP32 microcontroller, ultrasonic sensors, a servo motor, and a GPS module to monitor the bin and automate its operation.

The system communicates wirelessly with a Python-based desktop application, allowing users to monitor waste levels, view bin status, and identify the bin's geographical location.

## Features

- Automatic opening and closing of the bin lid
- Contactless lid operation using an ultrasonic sensor
- Real-time waste-level monitoring
- Waste-level indication through an LCD display
- Automatic full-bin detection and buzzer alert
- GPS-based bin location tracking
- Wi-Fi communication between ESP32 and desktop application
- Live waste-level and bin-status monitoring
- Desktop application with a graphical user interface
- Google Maps integration for viewing bin location

## Hardware Components

| **Component** | **Quantity** | **Purpose** |
| ---------------------- | :---: | ----------------------------------- |
| ESP32 Development Board | 1 | Main controller and Wi-Fi communication |
| HC-SR04 Ultrasonic Sensor | 2 | Detects approaching users and measures waste level |
| Servo Motor | 1 | Automatically opens and closes the bin lid |
| 16×2 LCD Display with I2C Module | 1 | Displays waste percentage and lid status |
| NEO-6M GPS Module | 1 | Determines the geographical location of the bin |
| Buzzer | 1 | Provides an alert when the bin is full |
| LEDs | As required | Visual status indication |
| Breadboard / Connecting Wires | As required | Circuit connections |

## Technologies Used

- Arduino IDE / C++
- ESP32
- Python
- Tkinter
- Wi-Fi
- HTTP
- JSON
- Google Maps

## System Architecture

The system consists of three main sections:

1. **Input:** Two HC-SR04 ultrasonic sensors detect approaching users and measure the waste level inside the bin. The GPS module provides location information.
2. **Processing:** ESP32 processes sensor readings, controls the servo motor and buzzer, updates the LCD display, and prepares data for transmission.
3. **Monitoring:** A Python Tkinter desktop application communicates with ESP32 over Wi-Fi using HTTP and receives data in JSON format. The application displays waste levels, bin status, and GPS location.


## Installation and Setup

### 1. Configure the ESP32

- Open the Arduino sketch using Arduino IDE.
- Update the Wi-Fi SSID and password in the code.
- Connect the required hardware components to the ESP32.
- Select the appropriate ESP32 board and COM port.
- Upload the code to the ESP32.

### 2. Configure the Python Application

- Open the Python desktop application.
- Update the ESP32 IP address in the application.
- Configure the login credentials as required.

### 3. Run the Python Application

```bash
python smart_bin_dashboard.py
```

**Note:** Make sure the ESP32 and computer are connected to the appropriate Wi-Fi network and that the correct ESP32 IP address is configured in the Python application.

## Working Principle

- The outer ultrasonic sensor detects a person approaching the bin.
- The servo motor automatically opens the lid.
- After the user disposes of the waste, the lid closes automatically.
- The inner ultrasonic sensor measures the waste level inside the bin.
- ESP32 processes the readings and updates the LCD display.
- When the bin reaches full capacity, the buzzer provides an alert.
- The GPS module provides the geographical location of the bin.
- ESP32 sends the collected information to the Python desktop application through Wi-Fi.
- The desktop application displays waste percentage, lid status, and location.
- Users can view the bin's location through Google Maps.

## Project Information

**Project:** Smart Bin Using ESP32

**Category:** Internet of Things (IoT) / Smart Waste Management

**Microcontroller:** ESP32

**Programming Languages:** C++ and Python

**Monitoring Interface:** Python Tkinter Desktop Application

**Communication:** Wi-Fi (HTTP and JSON)

---

