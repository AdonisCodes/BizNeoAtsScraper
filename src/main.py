from utils import BCOLORS
import requests
import json
from typing import Tuple
from random import randint
import time


state = {}
with open("state.json", "r") as f:
    state = json.load(f)

BASE_URL_BASIC = f"https://ats.bizneo.com/trabajar/{state['companySlug']}"
BASE_URL_ID = f"https://ats.bizneo.com/trabajar/{state['companyID']}"


def authenticate() -> Tuple[str, str]:
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


def getCompanyId():
    global BASE_URL_ID
    url = BASE_URL_BASIC + "/header"
    cookies, headers = authenticate()
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code < 399:
        recruiter_id = response.json()["recruiter"]["id"]
        if recruiter_id:
            state["companyID"] = recruiter_id
            BASE_URL_ID = f"https://ats.bizneo.com/trabajar/{state['companyID']}"
            with open("state.json", "w") as f:
                json.dump(state, f)
        else:
            print(BCOLORS.FAIL + "Failed to get companyID" + BCOLORS.ENDC)
            return None
    else:
        print(BCOLORS.FAIL + "Failed to get companyID" + BCOLORS.ENDC)
        return None


def getAllIds():
    cookies, headers = authenticate()
    if not cookies or not headers:
        print(BCOLORS.FAIL + "Authentication Failed!" + BCOLORS.ENDC)
        return None

    all_ids = []
    total_pages = state["previousPage"] + 1
    page = state["previousPage"] or 0
    time_until_sleep = randint(
        state["minTimeUntilSleep"][0], state["minTimeUntilSleep"][1]
    )
    while total_pages >= page:
        if time_until_sleep <= 0:
            sleep_total = randint(
                state["sleepDurationRange"][0], state["sleepDurationRange"][1]
            )
            time_until_sleep = randint(
                state["minTimeUntilSleep"][0], state["minTimeUntilSleep"][1]
            )
            print(
                BCOLORS.OKBLUE
                + f"Taking a break for {sleep_total} seconds"
                + BCOLORS.ENDC
            )
            print(
                BCOLORS.OKBLUE
                + f"Next Break in {time_until_sleep} seconds"
                + BCOLORS.ENDC
            )
            time.sleep(sleep_total)

        start = time.time()

        json_data = {
            "filters": {
                "age": [
                    16,
                    99,
                ],
                "experience": [
                    0,
                    40,
                ],
                "hidden": "false",
                "must_have_all_company_tags": False,
                "candidate_without_tags": False,
                "salary": {
                    "min": None,
                    "max": None,
                },
                "score": [
                    -10,
                    10,
                ],
                "stopped": "all",
                "update": [
                    0,
                    99,
                ],
                "tag_filter_option": "all_tag_selected",
                "candidates_without_forms": False,
                "candidates_without_videointerviews": False,
                "candidates_without_chat_bots": False,
                "order_user_by_chat_bot_score": False,
                "page": page + 1,
            },
        }

        response = requests.post(
            f"{BASE_URL_ID}/profile_pagination",
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        response_json = response.json()
        total_pages = response_json["profilePagination"]["totalPages"]
        page += 1
        print(BCOLORS.OKBLUE + f"Page {page} of {total_pages}" + BCOLORS.ENDC)
        all_ids.extend(response_json["candidateSlugs"])
        with open("all_ids.txt", "a") as f:
            f.write("\n".join(response_json["candidateSlugs"]) + "\n")

        with open("state.json", "w") as f:
            state["previousPage"] = page
            json.dump(state, f)

        print(BCOLORS.OKGREEN + f"Total IDs: {len(all_ids)}" + BCOLORS.ENDC)
        random_sleep_wait = randint(state["timeRange"][0], state["timeRange"][0]) / 3
        print(
            BCOLORS.OKBLUE
            + f"Sleeping for {random_sleep_wait} seconds to avoid detection!"
            + BCOLORS.ENDC
        )
        time.sleep(random_sleep_wait)
        request_took = time.time() - start
        time_until_sleep -= request_took
        print(BCOLORS.OKBLUE + f"Request took {request_took} seconds" + BCOLORS.ENDC)
        print(
            BCOLORS.OKBLUE
            + f"Time until next break: {time_until_sleep or 0}"
            + BCOLORS.ENDC
        )


def getMemberInfo(id: str) -> dict:
    cookies, headers = authenticate()
    if not cookies or not headers:
        print(BCOLORS.FAIL + "Authentication Failed!" + BCOLORS.ENDC)
        return None

    url = f"{BASE_URL_ID}/candidates/{id}"
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code < 399:
        response_json = response.json()
        with open("state.json", "w") as f:
            state["previousUser"] = id
            json.dump(state, f)
        
        with open(f"users/{id}.json", "w") as f:
            json.dump(response_json, f)
        
        for file in response_json['candidateAttachments']:
            file_id = file['id']
            candidate_id = id
            file_name = file['file']['name']
            url = file['file']['url'].replace("\u0026", "&")
            response = requests.get(url, headers=headers, cookies=cookies)
            with open(f"users/{candidate_id}_{file_id}_{file_name}", "wb") as f:
                f.write(response.content)
        return response_json

    else:
        print(BCOLORS.FAIL + f"Failed to get info for {id}" + BCOLORS.ENDC)
        return None


def main():
    if not state["companyID"]:
        print(BCOLORS.OKBLUE + "Getting Recruiter ID" + BCOLORS.ENDC)
        getCompanyId()

    if not state["previousUser"]:
        print(BCOLORS.OKBLUE + "Getting All IDs" + BCOLORS.ENDC)
        getAllIds()

    all_ids = []
    with open("all_ids.txt", "r") as f:
        all_ids = f.readlines()

    time_until_sleep = randint(
        state["minTimeUntilSleep"][0], state["minTimeUntilSleep"][1]
    )
    for id in all_ids:
        if time_until_sleep <= 0:
            sleep_total = randint(
                state["sleepDurationRange"][0], state["sleepDurationRange"][1]
            )
            time_until_sleep = randint(
                state["minTimeUntilSleep"][0], state["minTimeUntilSleep"][1]
            )
            print(
                BCOLORS.OKBLUE
                + f"Taking a break for {sleep_total} seconds"
                + BCOLORS.ENDC
            )
            print(
                BCOLORS.OKBLUE
                + f"Next Break in {time_until_sleep} seconds"
                + BCOLORS.ENDC
            )
            time.sleep(sleep_total)

        start = time.time()
        user_info = getMemberInfo(id)
        print(user_info)
        random_sleep_wait = randint(state["timeRange"][0], state["timeRange"][0])
        print(
            BCOLORS.OKBLUE
            + f"Sleeping for {random_sleep_wait} seconds to avoid detection!"
            + BCOLORS.ENDC
        )
        time.sleep(random_sleep_wait)
        request_took = time.time() - start
        time_until_sleep -= request_took
        print(BCOLORS.OKBLUE + f"Request took {request_took} seconds" + BCOLORS.ENDC)
        print(
            BCOLORS.OKBLUE
            + f"Time until next break: {time_until_sleep or 0}"
            + BCOLORS.ENDC
        )


if __name__ == "__main__":
    main()
