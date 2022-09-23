import json
import os
import time
import cv2

import numpy as np
import pandas as pd
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import tensorflow_hub as hub

from datetime import datetime
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

HOST = 'localhost'
PORT = 50000
BATCH_SIZE = 32
IMG_SIZE = 224

def make_dir(name):
  path = '/tmp/diplom/{0}/'.format(name)
  os.makedirs(path, exist_ok=True)
  return path

def take_images(work_dir):
  cam = cv2.VideoCapture(0)
  for i in range(5):
    _, image = cam.read()
    cv2.imwrite('{0}/image_{1}.jpg'.format(work_dir, i), image)
    time.sleep(0.1)
  del cam

def load_model(model_path):
    model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer': hub.KerasLayer})
    return model

def create_data_batches(x, y=None, batch_size=BATCH_SIZE, valid_data=False, test_data=False):
  if test_data:
    data = tf.data.Dataset.from_tensor_slices((tf.constant(x)))
    data = data.map(process_image)
    data_batch = data.batch(BATCH_SIZE)
    return data_batch
  elif valid_data:
    data = tf.data.Dataset.from_tensor_slices((tf.constant(x), tf.constant(y)))
    data = data.map(get_image_label)
    data_batch = data.batch(BATCH_SIZE)
    return data_batch
  else:
    data = tf.data.Dataset.from_tensor_slices((tf.constant(x), tf.constant(y)))
    data = data.shuffle(buffer_size=len(x))
    data = data.map(get_image_label)
    data_batch = data.batch(BATCH_SIZE)
  return data_batch

def process_image(image_path):
  image = tf.io.read_file(image_path)
  image = tf.image.decode_jpeg(image, channels=3)
  image = tf.image.convert_image_dtype(image, tf.float32)
  image = tf.image.resize(image, size=[IMG_SIZE, IMG_SIZE])
  return image

def get_image_label(image_path, label):
  image = process_image(image_path)
  return image, label

def most_common(predictions):
  return max(set(predictions), key=predictions.count)

def get_pred_label(prediction_probabilities):
    return unique_labels[np.argmax(prediction_probabilities)]

class HttpPostHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    now_date_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    work_dir = make_dir(now_date_time)
    take_images(work_dir)
    
    image_paths = [work_dir + image_name for image_name in os.listdir(work_dir)]
    custom_data = create_data_batches(image_paths, test_data=True)
    predictions = breed_identificator_model.predict(custom_data)
    labels = [get_pred_label(predictions[i]) for i in range(len(predictions))]
    most_common_breed = most_common(labels)

    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps({'label': most_common_breed}).encode())

def run(server_class=HTTPServer, handler_class=HttpPostHandler):
  server_address = (HOST, PORT)
  httpd = server_class(server_address, handler_class)
  try:
      httpd.serve_forever()
  except KeyboardInterrupt:
      httpd.server_close()

if __name__ == '__main__':
  breed_identificator_model = load_model('20220425-17481650908911-all-images.h5')
  labels_csv = pd.read_csv('labels.csv')
  string_labels = np.array(labels_csv.breed)
  unique_labels = np.unique(string_labels)
  run()
