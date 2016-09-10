import requests
import json
import base64

#Set the correct IP and port. Contact your admin :v
url = "http://192.168.0.8:8080"
headers = {'content-type': 'application/json'}

def test_classify(image_path):
    global url, headers

    encoded_string = None
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    # Example echo method
    payload = {
        "method": "getNutritionalInfo",
        "params": [{
            'image' : encoded_string,
            'file_extension' : 'png'
        }],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    return response



if __name__ == "__main__":
    print test_classify("image.png")
