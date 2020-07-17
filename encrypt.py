import cryptography
from cryptography.fernet import Fernet
import argparse
import logging
import PySimpleGUI as sg

logging.basicConfig(filename="encrypt.log", level=logging.INFO, filemode='w')

# Deprecating the command line argument parsing and using a GUI instead
# ap = argparse.ArgumentParser()
# ap.add_argument("-k", "--api_key", required=True, help="your Bing Image Search API Key")
# args = vars(ap.parse_args())

sg.theme('Topanga')
form = sg.FlexForm('API Key Encryption')
layout = [[sg.Text('API Key', text_color='white', size=(25, 1)), 
            sg.InputText("", text_color="white", key='api_key')],
        [sg.Submit("Encrypt"), sg.Cancel()],
	]
window = sg.Window('datasetBuilder', layout)
button,values = window.Read()

#Generate a random key we use for our encryption (type <bytes>)
key = Fernet.generate_key()
logging.info("Successfully generated , writing key to file...")

#Write the key to file so wes can use it for decryption later
try:
    file = open('key.key', 'wb')
    file.write(key)
except Exception as e:
    print(e)
    logging.info("Error occurred while writing cryptography key to file")
file.close()
logging.info("Key has been written to file")

logging.info("Encrypting api key...")
#Your API Key goes here to be encrypted
message = values["api_key"].encode()

#Use secret key authenticated cryptography
f = Fernet(key)
encrypted = f.encrypt(message)

try:
    file = open('api_key.encrypted', 'wb')
    file.write(encrypted)
except Exception as e:
    print(e)
    logging.info("Error occurred while writing encrypted api key to file")
file.close()

logging.info("Successfully encrypted and wrote api key to file")

sg.Popup("Succesfully encrypted your API Key :)", title="Success")
quit()