from utils import BCOLORS
import requests
import json


state = {}
with open("state.json", "r") as f:
    state = json.load(f)


def authenticate():
    if state["authentication"]["cookies"]:
        return (
            state["authentication"]["cookies"],
            state["authentication"]["headers"],
        )
    else:
        print(
            BCOLORS.FAIL
            + "No token found in state.json. Please Check the Video in the Readme For Instructions!"
            + BCOLORS.ENDC
        )
        return None, None


def get_company():
    url = ""
