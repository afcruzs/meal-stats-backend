from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from time import time
import base64
from subprocess import check_output
import os


generic_args = '$HOME/tensorflow/bazel-bin/tensorflow/examples/label_image/label_image --graph=/tmp/output_graph.pb --labels=/tmp/output_labels.txt --output_layer=final_result --image='

def create_args(file_name):
    return generic_args + file_name

def classify(base64Image, file_extension):
    time_as_string = str(time()).replace(".","")
    file_path = os.getcwd() + "/" + time_as_string + "." + "png"

    with open(file_path, "wb") as fh:
        fh.write(base64.decodestring(base64Image))

    args = create_args(file_path)
    output = check_output(args,shell=True)
    response = [class_result.split(":") for class_result in output.split(",")]
    os.remove(file_path)
    return response

@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b
    dispatcher["classify"] = classify

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)
