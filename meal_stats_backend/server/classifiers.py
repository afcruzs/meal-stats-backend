'''
Here should be a class for each classifier to use.
'''

import numpy as np
import tensorflow as tf
import os.path
from PIL import Image

'''
This is an adapted example from here:
https://github.com/eldor4do/Tensorflow-Examples/blob/master/retraining-example.py

There are some issues regarding to old versions of tensorflow, this has been
tested with 0.10.0 version, please use that version or above.
'''
class TFClassifer(object):
    '''
    Specify the model path and the labels path (absoulte path).
    '''
    def __init__(self, modelFullPath = '/tmp/output_graph.pb', labelsFullPath = '/tmp/output_labels.txt'):
        self.modelFullPath = modelFullPath
        self.labelsFullPath = labelsFullPath
        self.create_graph() # Creates graph from saved GraphDef.

    '''
    Internal method to load graph in tf.
    '''
    def create_graph(self):
        """Creates a graph from saved GraphDef file and returns a saver."""
        # Creates graph from saved graph_def.pb.
        with tf.gfile.FastGFile(self.modelFullPath, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

    def get_extension(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        return extension

    '''
    This method classifies a image stored in disk,
    the absoulte path should be used.
    '''
    def classifyWithPath(self, imagePath):
        answer = None

        if not tf.gfile.Exists(imagePath):
            tf.logging.fatal('File does not exist %s', imagePath)
            return answer
        extension = self.get_extension(imagePath)

        '''
        Workaround to support png encoding taken from here
        http://stackoverflow.com/questions/34484148/feeding-image-data-in-tensorflow-for-transfer-learning
        because inceptionV3 only supports JPEG images out-of-the-box.
        '''
        if extension == "jpg":
            image_data = tf.gfile.FastGFile(imagePath, 'rb').read()
            tensor_string = 'DecodeJpeg/contents:0'
        elif extension == 'png':
            image = Image.open(imagePath)
            image_data = np.array(image)[:, :, 0:3]  # Select RGB channels only.
            tensor_string = 'DecodeJpeg:0'
        else:
            raise ValueError("Not supported image type")


        with tf.Session() as sess:
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            predictions = sess.run(softmax_tensor, {tensor_string: image_data})
            predictions = np.squeeze(predictions)

            top_k = predictions.argsort()[-5:][::-1]  # Getting top 5 predictions
            f = open(self.labelsFullPath, 'rb')
            lines = f.readlines()
            labels = [str(w).replace("\n", "") for w in lines]
            predictions_ret = []
            for node_id in top_k:
                human_string = labels[node_id]
                score = predictions[node_id]
                predictions_ret.append((human_string, float(score)))
                #print('%s (score = %.5f)' % (human_string, score))

            #answer = labels[top_k[0]]
            return predictions_ret

        raise ValueError("Error with tensorflow session")
