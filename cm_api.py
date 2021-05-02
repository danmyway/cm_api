from urllib.request import Request, urlopen
from urllib.parse import urlencode
import hmac
import hashlib
import json
import argparse
import configparser

config = configparser.ConfigParser()
config.read('config.yaml')

apiKey = config.get("DEFAULT", "apiKey")
privateKey = config.get("DEFAULT", "privateKey")
clientID = config.get("DEFAULT", "clientID")
nonce = config.get("DEFAULT", "nonce")

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--fees",
    help="Check for current withdrawal fees.",
    action="store_true"
)
parser.add_argument(
    "-d", "--dump",
    help="Dumps current config file including your security credentials.A new config file needs to be configured.",
    action="store_true"
)
parser.add_argument(
    "-a",
    "--archive",
    help="Archives current config file.",
    action="store_true"
)
parser.add_argument(
    "-c",
    help="Changes path to config file."
)
parser.add_argument(
    "-p",
    "--pairs",
    help="Check for available currency pairs and returns an enumerated list",
    action="store_true"
)

def startup():
    #starts the program, creates configuration file
    try:
        with open(f"config.yaml", "x") as conf:
            conf.write(f"apiKey = \nprivateKey = \n clientID = \nnonce = 0")
    except FileExistsError:
        print("Creating config file skipped. Config file already exists.")

def log_count():
    count = ""
    try:
        log_file = open("log.txt")  # open file in read mode
        count_str = log_file.read()
        count = int(count_str)
        log_file.close()  # close file

    except FileNotFoundError:
        print("There is no log file.")
    except PermissionError:
        print("You are not permitted to read this file.")
    except ValueError:
        print("Log value needs to be integer.")

    try:
        log_file = open("log.txt", "w")  # open file again but in write mode
        count = int(count) + 1  # increase the count value by 1
        log_file.write(str(count))  # write count to file
        log_file.close()  # close file

    finally:
        return count


nonce = log_count()

def createSignature(clientId, apiKey, privateKey, nonce):
    message = str(nonce) + str(clientId) + apiKey
    signature = hmac.new(privateKey.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
    return signature.upper()


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

response_body_json = urlopen(request).read()
response_body = json.loads(response_body_json)

if isinstance(response_body["data"], dict):
    low_fee = format(response_body["data"]["low"], '.8f')
    high_fee = format(response_body["data"]["high"], '.8f')
    print(f"""Current low fee is {low_fee}.
    High priority fee is {high_fee}.""")

