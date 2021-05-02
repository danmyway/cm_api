import datetime
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import hmac
import hashlib
import json
import argparse
import configparser
import os
import shutil

config = configparser.ConfigParser()
# Reach for config file to read private credentials from.
config.read('config.yaml')

apiKey = config.get("DEFAULT", "apiKey")
privateKey = config.get("DEFAULT", "privateKey")
clientID = config.get("DEFAULT", "clientID")
nonce = config.get("DEFAULT", "nonce")

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--fees",
    help="Checks for current withdrawal fees.",
    action="store_true"
)
parser.add_argument(
    "-d",
    "--dump",
    help=f"""Dumps current config file including your security credentials. A new config file needs to be configured."
         Combine with 'cm_api.py -a' to archive current config file.""",
    action="store_true"
)
parser.add_argument(
    "-a",
    "--archive",
    help="Archives current config file.",
    action="store_true"
)
parser.add_argument(
    "-p",
    "--pairs",
    help="Checks for available currency pairs and returns an enumerated list.",
    action="store_true"
)

args = parser.parse_args()

def startup():
    #starts the program, creates configuration file
    try:
        with open(f"config.yaml", "x") as conf:
            conf.write(f"[DEFAULT]\napiKey = \nprivateKey = \n clientID = \nnonce = 0")
    except FileExistsError:
        print("Creating config file skipped. Config file already exists.")

def log_count():
    # Creates log.txt file to store no. of usages for correct nonce count.
    count = ""
    try:
        with open("log.txt") as log_file:  # open file in read mode
            count_str = log_file.read()
            count = int(count_str)

    except FileNotFoundError:
        print("There is no log file.")
    except PermissionError:
        print("You are not permitted to read this file.")
    except ValueError:
        print("Log value needs to be integer.")

    try:
        with open("log.txt", "w") as log_file: # open file again but in write mode
            count = int(count) + 1  # increase the count value by 1
            log_file.write(str(count))  # write count to file

    finally:
        return count


nonce = log_count()

def createSignature(clientId, apiKey, privateKey, nonce):
    message = str(nonce) + str(clientId) + apiKey
    signature = hmac.new(privateKey.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
    return signature.upper()

if args.fees:
    # Use startup() to create config file.
    startup()
    # Assign and encode signature to communicate with api services.
    params = {
        "clientId": clientID,
        "nonce": str(nonce),
        "signature": createSignature(clientID, apiKey, privateKey, nonce)
    }

    values = urlencode(params).encode("utf-8")

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    request = Request('https://coinmate.io/api/bitcoinWithdrawalFees', data=values, headers=headers)
    # Format json output from api service to human-readable format.
    response_body_json = urlopen(request).read()
    response_body = json.loads(response_body_json)

    if isinstance(response_body["data"], dict):
        low_fee = format(response_body["data"]["low"], '.8f')
        high_fee = format(response_body["data"]["high"], '.8f')
        print(f"""Current low fee is {low_fee}.
        High priority fee is {high_fee}.""")

if args.dump:
    print("WIP")

if args.archive:
    try:
        cwd = os.getcwd()
        archpath = os.path.join(cwd, "config_archive")
        os.mkdir(archpath)
    except FileExistsError:
        print(f"""Skipping mkdir. Directory already exists.""")
        pass
    now_raw = datetime.datetime.now()
    now = now_raw.strftime("%Y-%m-%d_%H:%M:%S")
    shutil.move(
        "config.yaml", os.path.join(
            archpath, str(now)+"_config.yaml"
        )
    )
    print(f"""Config file succesfully archived to {archpath}""")

if args.pairs:
    # Requests all available currency pairs through coinmate api.
    request = Request('https://coinmate.io/api/products')

    # Returns value in json, make into string and dissect only "data" list containing currency pairs.
    response_body_json = urlopen(request).read()
    response_body = json.loads(response_body_json)
    data = response_body["data"]

    # Make returned pairs into list. Replace dash with underscore for future usage.
    lspairs = [
        i["id"].replace("-", "_") for i in data
    ]

    # Make list of pairs into enumerated dictionary.
    dictpairs = {
        i: lspairs[i] for i in range(0, len(lspairs))
    }

    # Return said dictionary in somewhat pretty form
    for k, v in dictpairs.items():
        print(k, " : ", v)
