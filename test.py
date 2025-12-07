import json
from flask import Flask, render_template, request
from server import parse_listener_coordinates

app = Flask(__name__)

with open("listeners.json", "r", encoding="utf-8") as f:
    listeners = json.load(f)
    listeners = parse_listener_coordinates(listeners)


@app.route("/")
def index():
    view_state = request.args.get(
        "state", "NA"
    )  # query param like ?state=on to disable
    return render_template(
        "index.html",
        listeners=listeners,
        do_socket=False,
        view_state=view_state,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        use_reloader=False,
        debug=True,
    )
