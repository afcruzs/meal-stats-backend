from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from time import time
import base64
import os
import socket
from database.database import Database
from classifiers import TFClassifer

#DATABASE_HOST = "192.168.0.9"
DATABASE_HOST = "localhost"
DATABASE_PORT = 27017
#DATABASE_PORT = 21072
DATABASE_NAME = "mealStatsdb"

classifier = TFClassifer() #tensorflow based classifier powered by inceptionv3

'''
Taken from here:
http://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
'''
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

'''
This methods stores the base64 encoded version of the image.
'''
def store_file(base64Image, file_extension):

    time_as_string = str(time()).replace(".","")
    file_path = os.getcwd() + "/" + time_as_string + "." + file_extension

    with open(file_path, "wb") as fh:
        fh.write(base64.decodestring(base64Image))

    return file_path


'''
Remote procedure to return nutritional info.
Params:
    image : base 64 image encoded
    file_extension : name of the image file extension (without period)

'''
def getNutritionalInfo(params):
    print "Request arrived, passing to classifier..."
    base64Image = params['image']
    file_extension = params['file_extension']

    file_path = store_file(base64Image, file_extension)
    top_results = classifier.classifyWithPath(file_path)

    top_results.sort(key=lambda x: -x[1])

    results = [top_results[0]]
    i = 1
    while i < len(top_results):
        if top_results[i-1][1] - top_results[i][1] <= 0.1:
            results.append(top_results[i])
            i -= 1
        else:
            break

    print "Going to DB..."
    db_connection = Database(database=DATABASE_NAME, host=DATABASE_HOST, port=DATABASE_PORT)
    return_results = []
    print "Classifier results"
    for best_label, best_prob in results:
        print best_label, best_prob
        info = db_connection.getStats(best_label)
        print "Info returned: ", info
        if not info:
            return_results = {'name' : 'cant recognize picture', 'stats' : 'not recognized'}
        else:
            del info['_id']

    os.remove(file_path) #Removes tmp file :vvv
    return return_results


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
