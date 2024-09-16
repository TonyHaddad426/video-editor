from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from media import *
from dotenv import dotenv_values

config = dotenv_values(".env")

#DEPENDENCIES
# pip install flask restful
# pip install flask 

#jsonify is a method to convert dicts into JSON

app = Flask(__name__) # create Flask object 
cors = CORS(app)
api = Api(app) 

@app.route('/')
def welcome():
   return "Welcome!"



api.add_resource(VideoToGIF, "/videoToGIF") 
api.add_resource(GIFToVideo, "/GIFToVideo")
api.add_resource(VideoTrim, "/videoTrim") 
api.add_resource(Watermark, "/watermark") 
api.add_resource(RemoveAudio, "/removeAudio") 
api.add_resource(ExtractAudio, "/extractAudio") 
api.add_resource(AddText, "/addText") # not functional yet


if __name__ == '__main__': # the file that gets executed is always named __main__
    app.run(host=config.get("host"), port=config.get("port"), debug=True)

