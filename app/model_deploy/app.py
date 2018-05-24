from flask import Flask, request
from loadModel import get_styleswap

app = Flask(__name__)
model = get_styleswap()

@app.route('/')
def hello():
    return 'hello world'

@app.route('/', methods=['POST'])
def swap():
    #request.files['key'], request.form['string']
    content = request.form['content']
    style = request.form['style']
    img_inversed = model(content, style)
    return img_inversed


if __name__=='__main__':
    print("start server")
    app.run(host='0.0.0.0', debug=True)
    print("end server")