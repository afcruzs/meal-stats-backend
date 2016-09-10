import requests
import json
import base64

url = "http://localhost:4000"
headers = {'content-type': 'application/json'}

def test_classify(image_path):
    global url, headers

    encoded_string = None
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    # Example echo method
    payload = {
        "method": "classify",
        "params": [encoded_string],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    return response



def main():
    url = "http://localhost:4000"
    headers = {'content-type': 'application/json'}


    # Example echo method
    payload = {
        "method": "add",
        "params": ["23","12"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    print response

if __name__ == "__main__":
    #main()
    print test_classify("image.png")
