import speech_recognition as sr
from grovepi import *
from grove_rgb_lcd import *
import time
import pyrebase
import firebase_retrieve as fr
from uuid import getnode as get_mac

# Pin definitions
led = 3  # D3
fan = 2  # D2
buzzer = 4 #D4

mac = get_mac()
macString = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

# Initialize GPIO
def initialize_gpio():
    pinMode(led, "OUTPUT")
    pinMode(fan, "OUTPUT")
    pinMode(buzzer, "OUTPUT")

# Initialize Firebase (import pyrebase and provide your Firebase config here)
def initialize_firebase():
    config = {
    "apiKey" : "AIzaSyBoV8vhKkgEIMhVeeJZwOe4XWwPdSacLrk" ,
    "authDomain": "bait2123-iot-cb5df.firebaseapp.com",
    "databaseURL" : "https://bait2123-iot-cb5df-default-rtdb.asia-southeast1.firebasedatabase.app",
    "storageBucket": "iotlabbbb.appspot.com"
    }
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password("fxy1526@gmail.com", "0606x2002Y@")
    db = firebase.database()
    return db, user

def control_device(db,device_pin, device_state, event_log_name):
    digitalWrite(device_pin, device_state)
    
    log = {
        "timestamp": time.time(),
        "button": False,
        "voice": True,
        "remote": False,
        "event_type": f"{event_log_name} On" if device_state == 1 else f"{event_log_name} Off",
        "value": device_state
    }
    
    db.child(macString).child(f"{event_log_name}_event_log").push(log)

# Function to check for the wake word
def listen_for_wake_word(r):
    with sr.Microphone() as source:
        setRGB(0,255, 0)
        setText("Ready for \n'hello'...")
        audio = r.listen(source, timeout=5, phrase_time_limit=5)

    try:
        result = r.recognize_google(audio)
        if "hello" in result.lower():
            setRGB(0,255, 0)
            setText("Listening for \ncommands...")
            return True
        else:
            setRGB(255,0, 0)
            setText("Not recognize \nthe wake word.")
    except sr.UnknownValueError:
        setRGB(255,0, 0)
        setText("Couldn't \nunderstand.")
    except sr.RequestError as e:
        setRGB(255,0, 0)
        setText("No request \nfrom Google")

# Function to listen for commands
def listen_for_commands(r, db, led_state, fan_state):
    last_command_time = time.time()
    while True:
        with sr.Microphone() as source:
            setRGB(0,255, 0)
            setText("Listening for \ncommands...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)

        try:
            result = r.recognize_google(audio)
            if result:
                command_time = time.time()
                tokens = result.lower().split()  # Split and convert to lowercase

                if "on" in tokens:
                    if "everything" in tokens:
                        if led_state == 1 and fan_state==1:
                            setRGB(255,0, 0)
                            setText("Everything is\nalready On.")
                        else:
                            if fan_state == 0:
                                fan_state = 1
                                control_device(db, fan, fan_state, "fan")
                            if led_state == 0:
                                led_state = 1
                                control_device(db, led, led_state, "light")

                            setRGB(0, 255, 0)
                            setText("Everything is On.")
                    elif "fan" in tokens:
                        if fan_state == 1:
                            setRGB(255,0, 0)
                            setText("Fan is \nalready On.")
                        else:
                            fan_state = 1
                            setRGB(0,255, 0)
                            setText("Fan is On.")
                            control_device(db, fan, fan_state, "fan")
                    elif "light" in tokens:
                        if led_state == 1:
                            setRGB(255,0, 0)
                            setText("Light is \nalready On.")
                        else:
                            led_state = 1
                            setRGB(0,255, 0)
                            setText("Light is On.")
                            control_device(db, led, led_state, "light")
                    else:
                        setText("Wrong Command.")

                elif "off" in tokens:
                    if "everything" in tokens:
                        if led_state == 0 and fan_state == 0:
                            setRGB(255,0, 0)
                            setText("Everything is\nalready Off.")
                        else:
                            if fan_state == 1:
                                fan_state = 0
                                control_device(db, fan, fan_state, "fan")
                            if led_state == 1:
                                led_state = 0
                                control_device(db, led, led_state, "light")
                           
                            setRGB(0, 255, 0)
                            setText("Everything is Off.")
                    elif "fan" in tokens:
                        if fan_state == 0:
                            setRGB(255,0, 0)
                            setText("Fan is already Off.")
                        else:
                            fan_state = 0
                            setRGB(0,255, 0)
                            setText("Fan is Off.")
                            control_device(db, fan, fan_state, "fan")
                    elif "light" in tokens:
                        if led_state == 0:
                            setRGB(255,0, 0)
                            setText("Light is already Off.")
                        else:
                            led_state = 0
                            setRGB(0,255, 0)
                            setText("Light is Off.")
                            control_device(db, led, led_state, "light")
                    else:
                        setRGB(255,0, 0)
                        setText("Wrong Command.")

                else:
                    setRGB(255,0, 0)
                    setText("Wrong Command.")

                # Reset command timeout
                last_command_time = command_time

            else:
                setRGB(255,0, 0)
                setText("I didn't \ncatch that.")
        except sr.UnknownValueError:
            setRGB(255,0, 0)
            setText("I can't \nhear audio.")
        except sr.RequestError as e:
            setRGB(255,0, 0)
            setText(f"No request.")

        # Check for command timeout
        if time.time() - last_command_time >= 30:
            # If no command received for 30 seconds, break from command loop and listen for the wake word again
            break


# Main function
def main():
    initialize_gpio()
    db, user = initialize_firebase()

    # Initialize the recognizer and microphone
    r = sr.Recognizer()

    try:
        # Main loop
        while True:
            if listen_for_wake_word(r):
                # Set initial LED states
                led_state = fr.get_latest_value(db, macString, 'light_event_log')
                fan_state = fr.get_latest_value(db, macString, 'Fan_event_log')
                listen_for_commands(r, db, led_state, fan_state)  # Pass db as an argument
    except KeyboardInterrupt:
        # Turn off LEDs when the program is stopped
        digitalWrite(led, 0)
        digitalWrite(fan, 0)
        digitalWrite(buzzer, 0)
        # Turn off the LCD screen
        setText("")
        sys.exit(0)

if __name__ == "__main__":
    main()

