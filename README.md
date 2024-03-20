# IoT Voice Control System

## Overview

The IoT Voice Control System is a Python script designed to enable users to control devices such as lights and fans using voice commands. This system integrates with Firebase for data storage and retrieval and utilizes Raspberry Pi with GrovePi sensors for interaction with physical devices.

## Features

- Control lights and fans through voice commands
- Utilizes speech recognition for interpreting commands
- Integrates with Firebase for real-time data storage and retrieval
- Supports wake word detection for hands-free interaction

## Prerequisites

Before running the script, ensure you have the following:

- Raspberry Pi 4 with GrovePi sensors (I use led, fan, buzzer and mic)
- Python 3.x installed
- Required Python libraries (speech_recognition, grovepi, grove_rgb_lcd, pyrebase)
- Google Cloud Speech API credentials for speech recognition

## Setup

1. Clone the repository to your Raspberry Pi:

    ```
    git clone https://github.com/your-username/iot-voice-control.git
    ```

3. Obtain Google Cloud Speech API credentials and configure them in the script.

4. Initialize Firebase and update the Firebase configuration in the script.

5. Connect the GrovePi sensors according to the pin definitions in the script.

