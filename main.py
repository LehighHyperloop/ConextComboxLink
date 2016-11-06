from bs4 import BeautifulSoup
import json
import os
import paho.mqtt.client as mqtt
import requests
import time

SUBSYSTEM = "subsystem/inverter"

COMBOX_IP = "192.168.0.150"
COMBOX_USER = "admin"
COMBOX_PASS = os.environ["COMBOX_PASS"]

# Logic

# External and internal states
e_state = {
    "state": "STOPPED",
    "load": "0"
}
i_state = {
    "target_state": "STOPPED"
}

def logic_loop(client):
    # Send status updates
    client.publish(SUBSYSTEM, json.dumps(e_state))
    time.sleep(0.1);

# Setup scrape
login_page = None
while login_page == None or login_page.status_code == 301:
    login_page = requests.post("http://" + COMBOX_IP + "/login.cgi", data = { "submit": "Log In", "login_username": COMBOX_USER, "login_password": COMBOX_PASS })
    print login_page.status_code

main_page = requests.get("http://" + COMBOX_IP + "/main.html")
print main_page.content

# Setup client
client = mqtt.Client()
client.connect("192.168.0.100", 1883)
client.loop_start()

client.on_message = on_message
client.subscribe(SUBSYSTEM + "/#")

while True:
    logic_loop(client)

client.loop_stop()
