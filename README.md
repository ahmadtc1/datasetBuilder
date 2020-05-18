# datasetBuilder

🗂 A convenient utility for building your datasets with ease

  ## Live Demo


## How to Use it?
This utility requires Microsoft's Bing Image Search Api to function, so I've detailed the steps for obtaining your api key below

### Start by obtaining your API key by following the steps detailed below
* Head over to [Bing Image Search Api](https://azure.microsoft.com/en-us/try/cognitive-services/my-apis/?api=bing-image-search-api)

* Create a free Azure account (you'll get some cool perks and limited use free-resources as well as platform credit)

* Once you've created your account, return to the [APIs link](https://azure.microsoft.com/en-us/try/cognitive-services/my-apis/?api=bing-image-search-api)

* In the available APIs, "Add" the Bing Search APIs v7 API to obtain your api key

* Once you've added the API, you should able to see your api key in the "Your APIs" section towards the bottom. There should be two provided API keys. Copy either of them onto your clipboard.

### Install all the required pip packages
I've attached a requirements.txt to allow for easy package installation using the command below
```
pip3 install -r requirements.txt
```
### Encrypt your API key for secure usage

Download and run the encrypt.py file. This file takes your api key and encrypts it using a secure hashing algorithm for secure storage. Running this script will produce 2 files, 'api_key.encrypted' and 'key.key' in the same directory as your encrypt.py file.

You can start by checking the file's help flag for any additional arguments as shown below (this works for all of the python files)
```
python3 encrypt.py -h
```
which helps you identify how to use the file as such:
```
usage: encrypt.py [-h] -k API_KEY

optional arguments:
  -h, --help        show this help message and exit
  -k , --api_key 	your Bing Image Search API Key
```
then allowing you to use the file to generate your encrypted key
```
python3 -k YOUR_API_KEY

eg.
python3 -k a123456b78910
```

### Now Let's Generate Your Dataset :)
Start with the -h flag to see the command line arguments
```
python3 buildDataset.py -h
```
which helps you identify how to use the file as such:
```
usage: datasetBuilder.py [-h] -q QUERY -o OUTPUT

optional arguments:
  -h, --help     show this help message and exit
  -q , --query   query to search BING Image API for
  -o , --output  desired path to the output images directory
  -m , --max     desired dataset size
```
For example if I wanted to build a dataset of 300 cockatiel images in an output folder named dataset, I would run
```
python3 -q cockatiel -o dataset/ -m 300
```
Now sit back and watch your dataset appear :)


#### Issues
This tool has been tested however there's always possibility for some hidden errors which weren't caught. Feel free to open up an issue if you encounter any issues and I'll get to them asap



