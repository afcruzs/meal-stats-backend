from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from time import time
import base64
import os
import socket
from database.database import Database
from classifiers import TFClassifer
import argparse

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

    In case of error the returned dictionary has the key error and the value
    of the message. If there are details for internal logging (not for user showing)
    are stored in the propierty details.
'''

def getNutritionalInfo(params):
    try:
        print "Request arrived, passing to classifier..."
        for param in ('image', 'file_extension'):
            if param not in params:
                return {"error": "%s not in the parameters" % param}

        base64Image = params['image']
        file_extension = params['file_extension']

        file_path = store_file(base64Image, file_extension)
        try:
            top_results = classifier.classifyWithPath(file_path)
        except ValueError as e:
            return {"error": e.message}

        top_results.sort(key=lambda x: -x[1])

        results = [top_results[0]]
        difference_threshold = 0.1
        for i in xrange(1,len(top_results)):
            if top_results[i-1][1] - top_results[i][1] <= difference_threshold:
                results.append(top_results[i])
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
                return_results.append({'name' : best_label, 'stats' : 'not nutritional info'})
            else:
                return_results.append(info)

        os.remove(file_path) #Removes tmp file :vvv

        return return_results
    except Exception as e:
        return {"error": "Internal server error", "details": e.message}

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


parser = argparse.ArgumentParser()
parser.add_argument("--PORT", help="Port of the server")
parser.add_argument("--DATABASE_HOST", help="Host of the database")
parser.add_argument("--DATABASE_PORT", help="Port of the database")
parser.add_argument("--DATABASE_NAME", help="Database name")

if __name__ == '__main__':
    args = parser.parse_args()
    PORT = int(args.PORT) if args.PORT else 8080
    DATABASE_PORT = int(args.DATABASE_PORT) if args.DATABASE_PORT else 27017
    DATABASE_HOST = args.DATABASE_HOST if args.DATABASE_HOST else "localhost"
    DATABASE_NAME = args.DATABASE_NAME if args.DATABASE_NAME else "mealStatsdb"
    ip_address = get_ip_address()
    run_simple(ip_address, PORT, application)
