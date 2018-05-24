import tensorflow as tf

from models.style_swap_model import StyleSwapModel
from utils.config import process_config
from utils.utils import *
import numpy as np
import cv2
import base64
import scipy.misc as sc
from PIL import Image
from io import BytesIO

def loadImg(imgEncoded):
    min_side = 512
    #imgEncoded = base64.b64encode(img)
    img = base64.b64decode(imgEncoded)
    npimg = np.fromstring(img, dtype=np.uint8)
    cv_img = cv2.imdecode(npimg, 1)
    height, width = cv_img.shape[:2]
    if min(height, width) < min_side:
        print("height, width", height, width)
        rate = min_side * 1.0 / min(height, width)
        img = sc.imresize(cv_img, [int(height * rate), int(width * rate)])
    return cv_img

def get_styleswap():
    config = process_config('model.json')
    model = StyleSwapModel(config, [None, None])
    #load sess
    with tf.Graph().as_default():
        sess = tf.Session()
        sess.as_default()
        print(sess.list_devices())

        model.evaluate_height, model.evaluate_width = 1024, 1024
        model.init_evaluate_model()

        if model.init_op is not None:
            model.init_op(sess)
        model.load(sess)

    def swap(content, style):
        ci = loadImg(content)
        si = loadImg(style)
        """
        evaluate_size = ci.shape[:2]
        evaluate_size_si = si.shape[:2]
        print(evaluate_size, evaluate_size_si)
        #model.evaluate_height, model.evaluate_width = evaluate_size
        """

        inversed = sess.run(model.evaluate_op, feed_dict={model.input_image:ci, model.style_image:si,})
        inversed = np.array(inversed, dtype=np.uint8)
        inversed = Image.fromarray(inversed)

        # test save result. succeed!
        # inversed.save("here.jpg", format="JPEG")

        buffered = BytesIO()
        inversed.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        return img_str

    return swap
