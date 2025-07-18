from pythonosc.udp_client import SimpleUDPClient
import time
import threading
from tkinter import *
import customtkinter
from sys import argv
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

# Code to receive data from watch app by loic2665
# Original program HeartRateToWeb https://github.com/loic2665/HeartRateToWeb
# I merged the original python script with my script to create a UI and send the heart rate data to VRChat using their OSC support



# VRChat OSC Configuration
vrChatIp = "127.0.0.1"  # Local VRChat host IP
vrChatPort = 9000       # Default VRChat OSC port

# Configuration
textFilePath = "hr.txt"  # Path to your text file
messageInterval: int = 3
defaultMessageInterval: int = 3

# Variables
stop = False
heartRate: int = 0
maxHeartRate = 0
minHeartRate = 0


def write_hr(hr="0"):
    file = open('./hr.txt', 'w+')
    file.write("{}".format(hr))
    file.close()

def read_hr():
    file = open('./hr.txt', 'r')
    hr = file.readline()
    file.close()
    return hr

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class HeartBeatHandler(BaseHTTPRequestHandler):
    def _set_response(self, code):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        if self.path == "/hr":
            self._set_response(200)
            self.wfile.write(read_hr().encode('utf-8'))
        elif self.path == "/obs":
            self._set_response(200)
            self.wfile.write(open("./obs.html", "r").read().encode('utf-8'))
        elif self.path.startswith("/js/") or self.path.startswith("/css/"):
            self._set_response(200)
            self.wfile.write(open(".{}".format(self.path), "r").read().encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write("NOT FOUND".encode('utf-8'))


    def do_POST(self):
        if not stop:
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself

            self._set_response(200)
            self.wfile.write("OK".encode('utf-8'))
            data = post_data.decode('utf-8').split("=")
            print("Received BPM = {}".format(data[1]))
            write_hr(data[1])

def run(port, server_class=HTTPServer, handler_class=HeartBeatHandler):
    server_address = ("", port)

    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

def serverRun():
    print("Starting server...")
    port_arg = 6547

    while not stop:
        if len(argv) == 2:
            port_arg = argv[1]

        if len(argv) == 2:
            run(port=int(port_arg))
        else:
            run(port_arg)




def updateMaxHeartRate():
    global maxHeartRate
    print("Updating max heart rate...")
    Label_MaxHeartRate.configure(text="Max HR: {}".format(maxHeartRate))
    if heartRate > maxHeartRate:
        maxHeartRate = heartRate
        Label_MaxHeartRate.configure(text="Max HR: {}".format(maxHeartRate))

def updateMinHeartRate():
    global minHeartRate
    print("Updating min heart rate...")
    Label_MinHeartRate.configure(text="Min HR: {}".format(minHeartRate))
    if heartRate < minHeartRate:
        minHeartRate = heartRate
        Label_MinHeartRate.configure(text="Min HR: {}".format(minHeartRate))

def set_initial_min_max():
    global minHeartRate, maxHeartRate
    time.sleep(5)
    minHeartRate = heartRate
    maxHeartRate = heartRate




# Initialize OSC Client
client = SimpleUDPClient(vrChatIp, vrChatPort)

def read_and_send_text(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                message = line.strip()
                if message:
                    global heartRate
                    # Set Heart Rate Variable
                    heartRate = int(message)
                    Label_HeartRate.configure(text=(heartRate))
                    updateMaxHeartRate()
                    updateMinHeartRate()
                    # Send message to VRChat chat box
                    if message == "69":
                        client.send_message("/chatbox/input", ["♥ " + message + " Nice!", True])
                        print(f"Sent: {message}")
                    elif message == "96":
                        client.send_message("/chatbox/input", ["♥ " + message + " !eciN", True])
                        print(f"Sent: {message}")
                    elif message == "0":
                        client.send_message("/chatbox/input", ["♥ " + message + " ☠", True])
                    else:
                        client.send_message("/chatbox/input", ["♥ " + message + " BPM", True])  # True = Send immediately
                        print(f"Sent: {message}")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Functions to increase the message interval on button press
def increase_clicked_one(): # +1
    global messageInterval
    if messageInterval >= 1:
        messageInterval += 1
        print("Message Interval", messageInterval)
        Label_Interval.configure(text=str("Interval: {} Seconds".format(messageInterval)))

def increase_clicked_five(): # +5
    global messageInterval
    if messageInterval >= 1:
        messageInterval += 5
        print("Message Interval", messageInterval)
        Label_Interval.configure(text=str("Interval: {} Seconds".format(messageInterval)))

def increase_clicked_ten(): # +10
    global messageInterval
    if messageInterval >= 1:
        messageInterval += 10
        print("Message Interval", messageInterval)
        Label_Interval.configure(text=str("Interval: {} Seconds".format(messageInterval)))

# Functions to decrease the message interval on button press
def decrease_clicked_one(): # -1
    global messageInterval
    if messageInterval > 1:
        messageInterval -= 1
        print("Message Interval", messageInterval)
        Label_Interval.configure(text=str("Interval: {} Seconds".format(messageInterval)))

def decrease_clicked_five(): # -5
    global messageInterval
    if messageInterval > 1:
        messageInterval -= 5
        print("Message Interval", messageInterval)
        Label_Interval.configure(text=str("Interval: {} Seconds".format(messageInterval)))
def decrease_clicked_ten(): # -10
    global messageInterval
    if messageInterval > 1:
        messageInterval -= 10
        print("Message Interval", messageInterval)
        Label_Interval.configure(text=str("Interval: {} Seconds".format(messageInterval)))

# Functions to start and stop the program
def stop_program():
    global stop
    stop = True
    print("Program Stopped!")

def send_data():
    global stop
    stop = False
    while not stop:
        read_and_send_text(textFilePath)
        time.sleep(messageInterval)

def start_program():
    print("Program Started!")
    t = threading.Thread(target=send_data)
    t.start()
    t2 = threading.Thread(target=serverRun)
    t2.start()
    t3 = threading.Thread(target=set_initial_min_max)
    t3.start()

def restore_default():
    global messageInterval
    stop_program()
    messageInterval = defaultMessageInterval
    Label_Interval.configure(text=str(messageInterval))
    print("Program Reset!")

# Main window Properties
window = Tk()
window.title("OSC Heart Rate Monitor")
window.iconbitmap("R.ico")
window.geometry("800x350")
window.resizable(False, False)
window.configure(background = "#919191")

# Window Labels
Label_Main = customtkinter.CTkLabel( # Main Label
    master=window,
    text="Heart Rate To VRChat",
    font=("Arial", 23),
    text_color="#000000",
    height=30,
    width=250,
    corner_radius=0,
    bg_color="#919191",
    fg_color="#919191",
    )
Label_Main.place(x=280, y=0)

Label_HeartRate = customtkinter.CTkLabel( # Heart Rate Label
    master=window,
    text="HR: 999",
    font=("Courier New", 20),
    text_color="#000000",
    height=30,
    width=100,
    corner_radius=20,
    bg_color="#919191",
    fg_color="#ffffff",
    )
Label_HeartRate.place(x=340, y=40)

Label_MaxHeartRate = customtkinter.CTkLabel( # Maximum Heart Rate Label
    master=window,
    text="Max HR: 999",
    font=("Courier New", 20),
    text_color="#000000",
    height=30,
    width=100,
    corner_radius=20,
    bg_color="#919191",
    fg_color="#ffffff",
    )
Label_MaxHeartRate.place(x=460, y=40)

Label_MinHeartRate = customtkinter.CTkLabel( # Minimum Heart Rate Label
    master=window,
    text="Min HR: 999",
    font=("Courier New", 20),
    text_color="#000000",
    height=30,
    width=100,
    corner_radius=20,
    bg_color="#919191",
    fg_color="#ffffff",
    )
Label_MinHeartRate.place(x=170, y=40)


Label_Interval = customtkinter.CTkLabel( # Interval Label
    master=window,
    text="Interval: 3 Seconds",
    font=("Courier New", 14),
    text_color="#000000",
    height=30,
    width=180,
    corner_radius=0,
    bg_color="#919191",
    fg_color="#919191",
    )
Label_Interval.place(x=310, y=230)

# Buttons
Button_PlusOne = customtkinter.CTkButton( # Button to increase interval by 1
    master=window,
    text="+1",
    font=("undefined", 14),
    text_color="#000000",
    hover=True,
    hover_color="#949494",
    height=30,
    width=95,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#F0F0F0",
    command=increase_clicked_one,
    )
Button_PlusOne.place(x=460, y=100)

Button_PlusFive = customtkinter.CTkButton( # Button to increase interval by 5
    master=window,
    text="+5",
    font=("undefined", 14),
    text_color="#000000",
    hover=True,
    hover_color="#949494",
    height=30,
    width=95,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#F0F0F0",
    command=increase_clicked_five,
    )
Button_PlusFive.place(x=460, y=140)

Button_PlusTen = customtkinter.CTkButton( # Button to increase interval by 10
    master=window,
    text="+10",
    font=("undefined", 14),
    text_color="#000000",
    hover=True,
    hover_color="#949494",
    height=30,
    width=95,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#F0F0F0",
    command=increase_clicked_ten,
    )
Button_PlusTen.place(x=460, y=180)

Button_MinusOne = customtkinter.CTkButton( # Button to decrease interval by 1
    master=window,
    text="-1",
    font=("undefined", 14),
    text_color="#000000",
    hover=True,
    hover_color="#949494",
    height=30,
    width=95,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#F0F0F0",
    command=decrease_clicked_one,
    )
Button_MinusOne.place(x=240, y=100)

Button_MinusFive = customtkinter.CTkButton( # Button to decrease interval by 5
    master=window,
    text="-5",
    font=("undefined", 14),
    text_color="#000000",
    hover=True,
    hover_color="#949494",
    height=30,
    width=95,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#F0F0F0",
    command=decrease_clicked_five,
    )
Button_MinusFive.place(x=240, y=140)

Button_MinusTen = customtkinter.CTkButton( # Button to decrease interval by 10
    master=window,
    text="-10",
    font=("undefined", 14),
    text_color="#000000",
    hover=True,
    hover_color="#949494",
    height=30,
    width=95,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#F0F0F0",
    command=decrease_clicked_ten,
    )
Button_MinusTen.place(x=240, y=180)

Button_Reset = customtkinter.CTkButton( # Restore to default Values button
    master=window,
    text="Reset",
    font=("undefined", 14),
    text_color="#000000",
    hover=True,
    hover_color="#949494",
    height=30,
    width=95,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#F0F0F0",
    command=restore_default,
    )
Button_Reset.place(x=350, y=140)

Button_Start = customtkinter.CTkButton( # Start program button
    master=window,
    text="Start",
    font=("undefined", 30),
    text_color="#000000",
    hover=True,
    hover_color="#00a000",
    height=50,
    width=120,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#00be00",
    command=start_program,
    )
Button_Start.place(x=240, y=270)

Button_Stop = customtkinter.CTkButton( # Stop program button
    master=window,
    text="Stop",
    font=("undefined", 30),
    text_color="#000000",
    hover=True,
    hover_color="#a00000",
    height=50,
    width=120,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#919191",
    fg_color="#be0000",
    command=stop_program,
    )
Button_Stop.place(x=440, y=270)

#run main window
window.mainloop()
