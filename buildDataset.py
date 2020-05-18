import cryptography
from cryptography.fernet import Fernet
import requests
import numpy as np
import cv2
from requests import exceptions
import argparse
import os

#Handle argument parsing
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True, help="query to search BING Image API for")
ap.add_argument("-o", "--output", required=True, help="path to the output images directory")
ap.add_argument("-m", "--max", required=False, type=int, default=200, help="desired dataset size")
args = vars(ap.parse_args())

#Handle the intake and decryption of the previously encrypted api key
#Obtain the key used for encrypting
file = open('key.key', 'rb')
key = file.read()
file.close()

#Obtain the encrypted api key
file = open('api_key.encrypted', 'rb')
apikeyEncrypted = file.read()
file.close()

#Use secret key authenticated cryptography to decrypt
fernet = Fernet(key)

#Decrypt the encrypted api key
decrypted = fernet.decrypt(apikeyEncrypted)
decoded = decrypted.decode()
print("[INFO] your decrypted api key is {}".format(decoded))


#Set some constant variables and the endpoint url for the api
API_KEY = decoded
MAX_RESULTS = args["max"]
GROUP_SIZE = 50
URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"


#Prepare to handle most of the possible errors that can occur when digesting the api
EXCEPTIONS = set([IOError, FileNotFoundError, exceptions.RequestException, exceptions.HTTPError,
exceptions.ConnectionError, exceptions.Timeout])

#Store the query term in a variable for convenience and set search headers as well as parameters
query = args["query"]
headers = {"Ocp-Apim-Subscription-Key": API_KEY}
params = {"q": query, "offset": 0, "count": GROUP_SIZE}
path = None

#Query the api to request our data
print("[INFO] querying Bing API for {}".format(query))
data = requests.get(URL, headers=headers, params=params)
data.raise_for_status()
data = data.json()

#Grab the data from the response object
estimatedResultsNum = min(data["totalEstimatedMatches"], MAX_RESULTS)
print("[INFO] estimated number of results for {}: {}".format(query, estimatedResultsNum))

#Initialize the total num of downloaded images to 0
total = 0

#Loop over all the results returned in groups of results in the specified batch size at a time
for offset in range(0, estimatedResultsNum, GROUP_SIZE):
    #Update query parameters with the current offset and make the request
    print("[INFO] making request for group {} - {} of {}".format(offset, offset + GROUP_SIZE, estimatedResultsNum))

    params["offset"] = offset
    data = requests.get(URL, headers = headers, params = params)
    data.raise_for_status()
    data = data.json()
    print("[INFO] now saving images for group {} - {} of {}".format(offset, offset + GROUP_SIZE, estimatedResultsNum))

    for d in data["value"]:
        #Try to download the image
        try:
            #Query the url of the image
            print("[INFO] fetching: {}".format(d["contentUrl"]))
            data = requests.get(d["contentUrl"], timeout=30)

            #Build the path to the output image
            ext = d["contentUrl"][d["contentUrl"].rfind('.'):]
            path = os.path.sep.join([args["output"], "{}{}".format(str(total).zfill(8), ext)])

            file = open(path, 'wb')
            file.write(data.content)
            file.close()

        #Catch any errors preventing us from downloading the image
        except Exception as e:
            if (type(e) in EXCEPTIONS):
                print("[INFO] skipping : {}".format(d["contentUrl"]))
                continue

        #Try to load the image from the disk
        image = cv2.imread(path)

        if (image is None):
            print("[INFO] deleting: {}".format(path))
            os.remove(path)
            continue

        #Update the counter
        total += 1


