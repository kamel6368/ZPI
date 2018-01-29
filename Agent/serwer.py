import threading
from time import sleep

from flask import Flask, app, request


class Serv:

    def __init__(self, move, main):

        app = Flask("aaa")
        self.main = main
        self.move = move

        @app.route("/", methods=['POST'])
        def turn_left():
            json = request.get_json(force=True);
            processThread = threading.Thread(target=async_execute, args=(json,))
            processThread.start()
            return "OK"

        def async_execute(json):
            for action in json["actions"]:
                if action["type"] == "move":
                    print("jedz " + str(action["value"]))
                    self.move.go(action["value"])
                    # jedz do przodu
                if action["type"] == "turn":
                    print("skrec " + str(action["value"]))
                    self.move.turn(action["value"])
                    # skrec
                if action["type"] == "observe":
                    print("obserwuj " + json["ip"])
                    # obserwuj
                    self.main.observe()

        app.run(debug=True)