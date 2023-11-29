import base64
import io
import urllib.parse

import flask
import torch
import numpy as np
from PIL import Image

import load

app = flask.Flask(__name__)

def encode_image(img: Image.Image, format: str = "PNG") -> str:
    bytesIO = io.BytesIO()
    img.save(bytesIO, format=format)
    data = bytesIO.getvalue()
    string = base64.b64encode(data)
    url_string = urllib.parse.quote(string)
    data_url = f'data:image/{format.lower()};base64,{url_string}'
    return data_url

def decode_image(data_url: str) -> Image.Image:
    assert data_url.startswith('data:image')
    format, data = data_url.split(';')
    format = format[len('data:image/'):]
    assert data.startswith('base64,')
    data = data[len('base64,'):]
    data = urllib.parse.unquote(data)
    data_bytes = base64.b64decode(data)
    bytesIO = io.BytesIO(data_bytes)
    img = Image.open(bytesIO)
    img = remove_alpha(img)
    return img

def remove_alpha(img: Image.Image) -> Image.Image:
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        alpha = img.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, mask=alpha)
        return bg.convert('RGB')
    else:
        return img
    
    
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = load.load('scale2x.ckpt', scale=2).to(device)

@app.route('/')
def index():
    return flask.send_from_directory('client/dist', 'index.html')

@app.route('/<path:path>')
def home(path):
    return flask.send_from_directory('client/dist', path)

@app.route('/<path:path>.js')
def script(path):
    return flask.send_from_directory('client/dist', f'{path}.js', mimetype="application/javascript")

@app.route('/upscale', methods=['POST'])
def upscale():
    json = flask.request.get_json(force=True)
    url = json['image']
    img = decode_image(url)
    image_tensor = torch.tensor(np.array(img).transpose((2, 0, 1)))
    image_tensor = torch.unsqueeze(image_tensor, 0)
    image_tensor = image_tensor.to(device)
    with torch.no_grad():
        model.eval()
        upscaled = model(image_tensor).detach().cpu().numpy()[0].transpose((1, 2, 0))
    upscaled = np.clip(upscaled, 0, 255).astype('uint8')
    img = Image.fromarray(upscaled)
    url = encode_image(img)
    return flask.json.jsonify({'image': url})