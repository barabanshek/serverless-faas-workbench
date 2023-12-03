from concurrent import futures
import logging
import argparse
from time import time
import grpc
import json

from PIL import Image
import torch
from torchvision import transforms
from torchvision.models import resnet50
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




class Greeter(fibonacci_pb2_grpc.GreeterServicer):

    def __init__(self):
        self.imgs = ["800px-Porsche_991_silver_IAA.jpg", "512px-Cacatua_moluccensis_-Cincinnati_Zoo-8a.jpg", "800px-Sardinian_Warbler.jpg", "800px-7weeks_old.JPG", "800px-20180630_Tesla_Model_S_70D_2015_midnight_blue_left_front.jpg", "800px-Welsh_Springer_Spaniel.jpg", "800px-Jammlich_crop.jpg", "782px-Pumiforme.JPG"]
        self.cnt = 0
        self.model = resnet50(weights=None)
        self.model.load_state_dict(torch.load("resnet50-19c8e357.pth"))
        # self.model = torch.load("resnet50-19c8e357.pth")
        self.model.eval()
        self.class_idx = json.load(open("imagenet_class_index.json", 'r'))
        self.idx2label = [self.class_idx[str(k)][1] for k in range(len(self.class_idx))]
    
    def predict(self, img_path):
        start = time()
        input_image = Image.open(img_path)
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(input_image)
        input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model 
        output = self.model(input_batch)
        _, index = torch.max(output, 1)
        # The output has unnormalized scores. To get probabilities, you can run a softmax on it.
        # prob = torch.nn.functional.softmax(output[0], dim=0)
        # _, indices = torch.sort(output, descending = True)
        res = self.idx2label[index]
        latency = time() - start
        return latency, res

    def SayHello(self, request, context):
        if request.name == "record":
            img_filename = "image.jpg"
        elif request.name == "replay":
            img_filename= "animal-dog.jpg"
        else:
            self.cnt = (self.cnt + 1)%len(self.imgs)
            img_filename = self.imgs[self.cnt]

        lat, pred = self.predict(img_filename)

        msg = "fn: ResNet Img Recog | img: %s, pred: %s, lat: %f | runtime: python" % (img_filename, pred, lat)
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
