import cryptography
from cryptography.fernet import Fernet
import requests
import numpy as np
import cv2
from requests import exceptions
import argparse
import os
import os.path
from os import path
import logging
import PySimpleGUI as sg

#Set up for fresh logging
logging.basicConfig(filename="runtime.log", level=logging.INFO, filemode='w')

# Deprecating command-line argument parsing, moving to GUI
# Handle argument parsing
# ap = argparse.ArgumentParser()
# ap.add_argument("-q", "--query", required=True, help="query to search BING Image API for")
# ap.add_argument("-o", "--output", required=True, help="path to the output images directory")
# ap.add_argument("-m", "--max", required=False, type=int, default=200, help="desired dataset size")
# args = vars(ap.parse_args())

sg.theme('Topanga')

form = sg.FlexForm('dataset builder params')

layout =[[sg.Text('Query', text_color='white', size=(25, 1)), 
            sg.InputText("", text_color="white", key='query')],
	[sg.Text('Dataset Size', text_color='white', size=(25, 1)),
            sg.InputText("", text_color="white", key='datasetSize')],
    [sg.Text('Output Folder', text_color='white', size=(25, 1)),
            sg.InputText("", text_color="white", key='output')],
    [sg.Submit(), sg.Cancel()],
	]
window = sg.Window('datasetBuilder', layout)

button,values = window.Read()

print(button, values['query'],values['datasetSize'] )
# quit()

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
logging.info("your decrypted api key is: %s", decoded)
print("[INFO] your decrypted api key is: {}".format(decoded))


#Set some constant variables and the endpoint url for the api
API_KEY = decoded
MAX_RESULTS = int(values["datasetSize"])
GROUP_SIZE = 50 if MAX_RESULTS >= 50 else MAX_RESULTS
URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"


#Prepare to handle most of the possible errors that can occur when digesting the api
EXCEPTIONS = set([IOError, FileNotFoundError, exceptions.RequestException, exceptions.HTTPError,
exceptions.ConnectionError, exceptions.Timeout])

#TODO add check to see if input filepath (directory exists), if not then create directory to prevent errors

#Store the query term in a variable for convenience and set search headers as well as parameters
query = values["query"]
headers = {"Ocp-Apim-Subscription-Key": API_KEY}
params = {"q": query, "offset": 0, "count": GROUP_SIZE}
filepath = None
outputPath = values["output"]

if not os.path.exists(outputPath):
    logging.info("Output directory does not exist. Creating output directory")
    os.mkdir(outputPath)
    logging.info("Successfully created output directory: %s", outputPath)
else:
    logging.info("Output directory %s exists", outputPath)

#Query the api to request our data
print("[INFO] querying Bing API for {}".format(query))
logging.info("querying Bing API for %s", query)
data = requests.get(URL, headers=headers, params=params)
data.raise_for_status()
data = data.json()

#Grab the data from the response object
estimatedResultsNum = min(data["totalEstimatedMatches"], MAX_RESULTS)
print("[INFO] estimated number of results for {}: {}".format(query, estimatedResultsNum))
logging.info("estimated number of results for %s: %d", query, estimatedResultsNum)

#Initialize the total num of downloaded images to 0
total = 0

#Loop over all the results returned in groups of results in the specified batch size at a time
for offset in range(0, estimatedResultsNum, GROUP_SIZE):
    #Update query parameters with the current offset and make the request
    print("[INFO] making request for group {} - {} of {}".format(offset, offset + GROUP_SIZE, estimatedResultsNum))
    logging.info("making request for group %d - %d of %d", offset, offset + GROUP_SIZE, estimatedResultsNum)
    params["offset"] = offset
    data = requests.get(URL, headers = headers, params = params)
    data.raise_for_status()
    data = data.json()
    print("[INFO] now saving images for group {} - {} of {}".format(offset, offset + GROUP_SIZE, estimatedResultsNum))
    logging.info("now saving images for group %d - %d of %d", offset, offset + GROUP_SIZE, estimatedResultsNum)
    for d in data["value"]:
        #Try to download the image
        try:
            #Query the url of the image
            logging.info("[%d / %d] fetching : %s", total, estimatedResultsNum, d["contentUrl"])
            data = requests.get(d["contentUrl"], timeout=15)

            #Build the path to the output image
            contentUrl = d["contentUrl"]
            periodIndex = contentUrl.rfind(".")
            ext = contentUrl[periodIndex : periodIndex + 4]

            if (ext[-1] != 'g' and ext[-1] != 'G'):
                ext = contentUrl[periodIndex : periodIndex + 5]

            filepath = os.path.sep.join([values["output"], "{}{}".format(str(total).zfill(8), ext)])
            logging.info("[%d / %d] filesave path: %s", total, estimatedResultsNum, filepath)

            file = open(filepath, 'wb')
            file.write(data.content)
            file.close()

        #Catch any errors preventing us from downloading the image
        except Exception as e:
            if (type(e) in EXCEPTIONS):
                logging.info("skipping %s", d["contentUrl"])
                continue

        #Try to load the image from the disk
        image = cv2.imread(filepath)

        if (image is None):
            try:
                logging.info("deleting %s", filepath)
                os.remove(filepath)
                continue
            except Exception as e:
                logging.error("failed to remove file, path does not exist")
            

        #Update the counter
        total += 1

print("[INFO] DONE SAVING YOUR DATASET. Enjoy :)")
logging.info("Completed saving dataset")
sg.Popup("Successfully built your {} dataset :)".format(values['query']), title="Success")

quit()