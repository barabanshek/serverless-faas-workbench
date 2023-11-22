from concurrent import futures
import logging
import argparse
from time import time
import grpc

from squeezenet import SqueezeNet
from tensorflow.python.keras.preprocessing import image
from tensorflow.python.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
from time import time

from grpc_reflection.v1alpha import reflection

from proto.fibonacci import fibonacci_pb2
import fibonacci_pb2_grpc
import re
import os
import sys

print("python version: %s" % sys.version)
print("Server has PID: %d" % os.getpid())
GRPC_PORT_ADDRESS = os.getenv("GRPC_PORT")

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
args = parser.parse_args()


def predict(img_path):
    start = time()
    model = SqueezeNet(weights='imagenet')
    img = image.load_img(img_path, target_size=(227, 227))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    res = decode_predictions(preds)
    latency = time() - start
    return latency, res

class Greeter(fibonacci_pb2_grpc.GreeterServicer):

    def __init__(self):
        self.img_names = ["animal-dog.jpg", "image.jpg"]
        self.img_count = 0
    
    def SayHello(self, request, context):
        img_path = self.img_names[self.img_count%len(self.img_names)]
        lat, res = predict(img_path)
        self.img_count += 1
        msg = "fn: Model Serving CNN | input: %s, pred: %s, lat: %i | runtime: python" % (img_path, res, lat)
        return fibonacci_pb2.HelloReply(message=msg)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    fibonacci_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    print("Enabling Reflection")
    SERVICE_NAMES = (
        fibonacci_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    address = ('[::]:' + GRPC_PORT_ADDRESS if GRPC_PORT_ADDRESS else  '[::]:50051')
    server.add_insecure_port(address) 

    logging.info("Start server: listen on : " + address)

    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
