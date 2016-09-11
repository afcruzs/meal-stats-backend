from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from time import time
import base64
from subprocess import check_output
import os
import socket
from database.database import Database

#DATABASE_HOST = "192.168.0.9"
DATABASE_HOST = "localhost"
DATABASE_PORT = 27017
#DATABASE_PORT = 21072
DATABASE_NAME = "mealStatsdb"

'''
    This script inits the server and listens in the 8080 port
    to resolve classify images requests.
'''

#Is done by executing tensorflow c++ binaries
generic_args = '$HOME/tensorflow/bazel-bin/tensorflow/examples/label_image/label_image --graph=/tmp/output_graph.pb --labels=/tmp/output_labels.txt --output_layer=final_result --image='


'''
Taken from here:
http://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
'''
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

'''
Creates a valid command to execute in terminal.
'''
def create_args(file_name):
    return generic_args + file_name


'''
Remote procedure to classify images.
Params:
    image : base 64 image encoded
    file_extension : name of the image file extension (without period)

'''
def classify(params):
    base64Image = params['image']
    file_extension = params['file_extension']

    time_as_string = str(time()).replace(".","")
    file_path = os.getcwd() + "/" + time_as_string + "." + file_extension

    with open(file_path, "wb") as fh:
        fh.write(base64.decodestring(base64Image))

    args = create_args(file_path)
    output = check_output(args,shell=True)
    response = [class_result.split(":") for class_result in output.split(",")]
    os.remove(file_path)
    return response

def getNutritionalInfo(params):
    print "Request arrived, passing to classifier..."
    response = classify(params)
    top_results = ((label, float(rate))for label, rate  in response)
    best_label, best_prob = max(top_results, key=lambda x: x[1])
    print "Classifier results", best_label, best_prob
    print "Going to DB..."
    db_connection = Database(database=DATABASE_NAME, host=DATABASE_HOST, port=DATABASE_PORT)
    info = db_connection.getStats(best_label)
    print "Info returned: ", info
    if not info:
        return {'name' : 'cant recognize picture', 'stats' : 'not recognized'}
    del info['_id']
    return [info]


'''
Main server application method, add the needed services
in the dispatcher.
'''
@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b
    dispatcher["getNutritionalInfo"] = getNutritionalInfo

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    ip_address = get_ip_address()
    PORT = 8080
    run_simple(ip_address, PORT, application)
