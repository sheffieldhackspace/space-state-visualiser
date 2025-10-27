import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
import jq

app = Flask(__name__)

app.config["MQTT_BROKER_URL"] = "mosquitto.shhm.uk"  # use the free broker from HIVEMQ
app.config["MQTT_BROKER_PORT"] = 1883  # default port for non-tls connection
app.config["MQTT_KEEPALIVE"] = (
    5  # set the time interval for sending a ping to the broker to 5 seconds
)
app.config["TEMPLATES_AUTO_RELOAD"] = True

mqtt = Mqtt(app)
socketio = SocketIO(app)

# can generate this from boilerplate with something like
# while read -r id; do
#   jq -n --arg id "${id}" '{id: $id, topic:"", msgON: "", msgOFF: ""}'
# done <<<$(ls static/icons/ | grep '.NA.' | sed 's+\.NA\.png++') | jq --slurp
with open("listeners.json", "r", encoding="utf-8") as f:
    listeners = json.load(f)


@app.route("/")
def index():
    for listener in listeners:
        if listener["topic"] == "":
            continue
        mqtt.subscribe(listener["topic"])
    return render_template("index.html", listeners=listeners)


@app.route("/listeners")
def getlisteners():
    colnames = ["id", "lastState", "topic", "jq", "msgON", "msgOFF"]
    for listener in listeners:
        for key in listener.keys():
            if key not in colnames:
                colnames.append(key)
    return render_template("table.html", colnames=colnames, records=listeners)


@app.route("/listeners.json")
def getlistenersjson():
    return listeners


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    # this doesn't do anything sometimes, see
    # https://stackoverflow.com/questions/64592277/flask-mqtt-on-connect-is-never-called-when-used-with-socketio
    # mqtt.subscribe("#")
    for listener in listeners:
        if listener["topic"] == "":
            continue
        mqtt.subscribe(listener["topic"])
    pass


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    for listener in listeners:
        if message.topic != listener["topic"]:
            continue

        payload = message.payload.decode()
        app.logger.info(
            "got message for %s: //%s %s", listener["id"], message.topic, payload
        )

        if jk := listener.get("jq", ""):
            payloadjson = json.loads(payload)
            payload = jq.compile(jk).input_value(payloadjson).first()

        # convert comparisons to arrays
        if not isinstance(listener["msgON"], list):
            listener["msgON"] = [listener["msgON"]]
        if not isinstance(listener["msgOFF"], list):
            listener["msgOFF"] = [listener["msgOFF"]]

        if payload in listener["msgON"]:
            listener["lastState"] = "on"
            socketio.emit("status-update", data=[listener, "on"])
        elif payload in listener["msgOFF"]:
            listener["lastState"] = "off"
            socketio.emit("status-update", data=[listener, "off"])
        else:
            listener["lastState"] = "NA"
            socketio.emit("status-update", data=[listener, "NA"])

        save_listener_state()


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


def save_listener_state():
    states = []
    for listener in listeners:
        if ls := listener.get("lastState"):
            states.append({"listenerid": listener["id"], "lastState": ls})
    with open("history.json", "w", encoding="utf-8") as file:
        json.dump(states, file)


def load_listener_state():
    with open("history.json", "r", encoding="utf-8") as file:
        states = json.load(file)
    for state in states:
        for listener in listeners:
            if listener["id"] == state["listenerid"]:
                listener["lastState"] = state["lastState"]
    print(listeners)


load_listener_state()

if __name__ == "__main__":
    mqtt.init_app(app)
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        use_reloader=False,
        debug=True,
    )
