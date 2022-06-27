import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
from flask import Flask, Response
import cv2

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)    # open webcam

    def __del__(self):
        self.video.release()

    def _resizeImage(self, img, percent):
        width = int(img.shape[1] * percent / 100)
        height = int(img.shape[0] * percent / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        return img, dim

    def get_frame(self):
        success, image = self.video.read()
        scale_percent = 50 # percent of original size
        image, _ = self._resizeImage(image, scale_percent)
        image = cv2.flip(image, 1)   # flip horizontally
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

@server.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

app.layout = html.Div([
    html.H2("Web Camera Output"),
    html.Img(src="/video_feed", 
                    style={
                        'backgroundColor':'darkslategray',
                        'color':'lightsteelblue',
                        'height':'20%',
                        'margin-left':'10px',
                        'width':'20%',
                        'text-align':'center',
                        'display':'inline-block'
                        }),

    html.H2('Interactive normal distribution'),
    dcc.Graph(id="graph", style={
                        'backgroundColor':'darkslategray',
                        'color':'lightsteelblue',
                        'height':'35%',
                        'margin-left':'10px',
                        'text-align':'center',
                        'width':'40%',
                        'display':'inline-block'
               }),

    html.H4("Mean:"),
    dcc.Slider(id="mean", min=-3, max=3, value=0, 
               marks={-3: '-3', 3: '3'}),
    html.H4("Standard Deviation:"),
    dcc.Slider(id="std", min=1, max=3, value=1, 
               marks={1: '1', 3: '3'}),
])

@app.callback(Output("graph", "figure"), Input("mean", "value"), Input("std", "value"))
def display_color(mean, std):
    data = np.random.normal(mean, std, size=500) # replace with your own data source
    fig = px.histogram(data, range_x=[-10, 10])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


'''
All 3 files running on the NUC:
    publisher.py  publishing the camera frames to a ros topic
    subscriber.py fetching the camera frames from the ros topic and sending it on the socket server
    dashboard.py  recieves images from the socket and displays on the web browser.

longterm: join the subscriber.py with dashboard.py and remove socket

'''