import cryptography
from cryptography.fernet import Fernet
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-k", "--api_key", required=True, help="your Bing Image Search API Key")
args = vars(ap.parse_args())


#Generate a random key we use for our encryption (type <bytes>)
key = Fernet.generate_key()

#Write the key to file so we can use it for decryption later
file = open('key.key', 'wb')
file.write(key)
file.close()

#Your API Key goes here to be encrypted
message = args["api_key"].encode()

#Use secret key authenticated cryptography
f = Fernet(key)
encrypted = f.encrypt(message)

file = open('api_key.encrypted', 'wb')
file.write(encrypted)
file.close()