# library
import requests
import json

# firebase url
url = 'https://raw-data-mart-default-rtdb.firebaseio.com/'

start_file = './start_file.json'

def start():
    requests.put(url+'.json',json = {})
    with open(start_file) as json_file:
        start_data = json.load(json_file)
        
    a = requests.put(url+'.json',json = start_data)
    print(a)
    
start()

