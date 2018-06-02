import requests
import base64
import numpy as np
from PIL import Image
from io import BytesIO

if __name__=="__main__":

    with open("0.jpg", "rb") as f:
        content = f.read()
    with open("1.jpg", "rb") as f:
        style = f.read()

    content = base64.b64encode(content)
    style  = base64.b64encode(style)
    data = {'content': content, 'style': style}
    r = requests.post("http://47.92.69.29:5000", data=data)

    img = Image.open(BytesIO(base64.b64decode(r.text)))

    img.show()
