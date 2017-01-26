from bs4 import BeautifulSoup
import json
import os
import paho.mqtt.client as mqtt
import requests
import time

SUBSYSTEM = "subsystem/inverters"

COMBOX_IP = "192.168.0.150"
COMBOX_USER = "admin"
COMBOX_PASS = os.environ["COMBOX_PASS"]

SESSION = requests.Session() #session to maintain login cookies

# Logic

# External and internal states
e_state = {
    "state": "STOPPED",
    "load": "0"
}
i_state = {
    "target_state": "STOPPED"
}

# puts all the data in the list *fields* into a json object
# with two keys (device names XW8548-61 and XW8548-61), containing all the data
# then publishes it to subsystem/inverter
def send_inverter_json(fields):
    inverter1_data = [x for x in fields if "400858" in x]
    inverter2_data = [x for x in fields if "385892" in x]
    inverter_json = {}
    inverter1_json = {}
    inverter2_json = {}

    inverter_json = {
        "state": "RUNNING",
        "inverters": { "0": {}, "1": {} }
    }

    try:
        for i in inverter1_data:
            i = i.replace("(400858)", "")
            halves = i.split("=")
            inverter1_json[halves[0]] = halves[1]

        inverter_json["inverters"]["0"] = {
            "voltage": inverter1_json["XW.VDCIN"],
            "wattage": inverter1_json["XW.PACLOAD2"],
            "temp": inverter1_json["XW.TBATT"],
        }
    except:
        pass

    try:
        for i in inverter2_data:
            i = i.replace("(385892)", "")
            halves = i.split("=")
            inverter2_json[halves[0]] = halves[1]

        inverter_json["inverters"]["1"] = {
            "voltage": inverter2_json["XW.VDCIN"],
            "wattage": inverter2_json["XW.PACLOAD2"],
            "temp": inverter2_json["XW.TBATT"],
        }
    except:
        pass

    print inverter_json, "\n\n"
    client.publish(SUBSYSTEM, json.dumps(inverter_json))

#scrape status from combox page and send it out
def logic_loop(client):
    client.publish(SUBSYSTEM, json.dumps(e_state))
    values_URL = "http://" + COMBOX_IP +"/gethandler.json?name=XBGATEWAY.VARLIST"
    values = SESSION.get(values_URL).content
    values = values.replace("&#0D;&#0A", "")
    values_json = json.loads(values)

    intermediate = values_json["values"]
    intermediate = intermediate["XBGATEWAY.VARLIST"]
    values = intermediate.split(";")

    send_inverter_json(values)
    time.sleep(0.1);

#needed for the interface, doesn't really do anything as of now
def on_message(client, unknown, message):
    pass

# Setup scrape
login_page = None
while login_page == None or login_page.status_code == 301:
    login_page = SESSION.post("http://" + COMBOX_IP + "/login.cgi", data = { "submit": "Log In", "login_username": COMBOX_USER, "login_password": COMBOX_PASS })
    # print login_page.status_code


# main_page = SESSION.get("http://" + COMBOX_IP + "/main.html")
# print main_page.content


# Setup client
client = mqtt.Client()
client.connect("192.168.0.100", 1883)
client.loop_start()

client.on_message = on_message
client.subscribe(SUBSYSTEM + "/#")

while True:
    logic_loop(client)

client.loop_stop()
