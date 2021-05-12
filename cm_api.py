import datetime
import sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import hmac
import hashlib
import json
import argparse
import configparser
import os
import shutil


cwd = os.getcwd()
configfile = "config.yaml"
logfile = "log.txt"

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--initiate",
    help=f"""Initiates the script and creates configuration file in {cwd} for further usage.""",
    action="store_true"
)
parser.add_argument(
    "-f",
    "--fees",
    help="Checks for current withdrawal fees.",
    action="store_true"
)
parser.add_argument(
    "-d",
    "--dump",
    help="""***WIP***
    Dumps current config file including your security credentials. A new config file needs to be configured."
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

def xconf():
    with open(configfile, "x") as conf:
        conf.write("[DEFAULT]\napiKey = \nprivateKey = \nclientID = ")
    print(f"Created an empty configuration file in {cwd}/{configfile}.")

def startup():
    # Starts the program, creates configuration file
    try:
        xconf()
    except FileExistsError:
        print("Creating config file skipped. Config file already exists.")
        raise FileExistsError


def readconfig():
    config = configparser.ConfigParser()
    # Reach for config file to read private credentials from.
    config.read(configfile)

    apiKey = config.get("DEFAULT", "apiKey")
    privateKey = config.get("DEFAULT", "privateKey")
    clientID = config.get("DEFAULT", "clientID")

    return apiKey, privateKey, clientID


def log_count():
    # Creates log.txt file to store no. of usages for correct nonce value.
    count = 0
    try:
        with open(logfile) as log_file:  # open file in read mode
            count_str = log_file.read()
            count = int(count_str)
        with open(logfile, "w") as log_file:  # open file again but in write mode
            count = int(count) + 1  # increase the count value by 1
            log_file.write(str(count))  # write count to file

    except FileNotFoundError:
        print("There is no log file.")
    except PermissionError:
        print("You are not permitted to handle this file.")
    except ValueError:
        print("Log value needs to be integer.")

    finally:
        return count


nonce = log_count()


def createSignature(clientId, apiKey, privateKey, nonce):
    apiKey, privateKey, clientID = readconfig()
    message = str(nonce) + str(clientId) + apiKey
    signature = hmac.new(privateKey.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
    return signature.upper()

def archive():
    try:
        archpath = os.path.join(cwd, "config_archive")
        os.mkdir(archpath)
    except FileExistsError:
        print(f"Skipping mkdir. Directory already exists.")
        pass
    now_raw = datetime.datetime.now()
    now = now_raw.strftime("%Y-%m-%d_%H:%M:%S")
    rename_config = f"{now:s}_{configfile}"
    shutil.move(
        configfile, os.path.join(
            archpath, rename_config
        )
    )
    print(f"Config file succesfully archived to {archpath}/{rename_config}")


if len(sys.argv) <= 1:
    print("Please use any of the available parameters.\nRefer to --help for valid options.")


if args.initiate:
    try:
        startup()
        log_count()
    except FileExistsError:
        print("Nothing to do! Configuration file already created.")
    else:
        print(
            f"""Initialization finalized.
            \nPlease visit https://coinmate.io/pages/secured/accountAPI.page to generate your API key.
            \nThen assign your credentials to {cwd}/{configfile}
""")


if args.fees:
    # Unpack tuple returned from readconfig() containing configfile credentials
    apiKey, privateKey, clientID = readconfig()
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
        print(f"Current low fee is {low_fee}.\nHigh priority fee is {high_fee}.")

if args.dump:
    # Check for existing --archive argument.
    if args.archive:
        print(f"Checking for {configfile} archivation....")
    else:
        affir = input(f"{configfile} has not been archived. \nWrite 'a' to archive current {configfile}"
                      f"\nWrite 'yes' if you want to proceed without archiving.")
        while True:
            if affir.lower() == "a":
                try:
                    archive()
                    break
                except PermissionError:
                    print(f"There might be problem with permissions in {cwd}!")
            if affir.lower() == "yes":
                xconf()
                break
            else:
                print("Please input valid option!")




if args.archive:
    try:
        archive()
    except PermissionError:
        print(f"There might be problem with permissions in {cwd}!")


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
