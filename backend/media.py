from flask_restful import Resource, reqparse
from flask import request, abort
from subprocess import run, PIPE
import requests
import uuid
import time
from services.s3client import S3Client
from services.timestamp import timestampToSeconds
from datetime import datetime
s3client = S3Client()
time = timestampToSeconds()

class GIFToVideo(Resource):
    parser = reqparse.RequestParser() # initialize new object to parse request 
    # parser.add_argument('start', required=True, help="This field can't be blank")
    # parser.add_argument('end', required=True, help="This field can't be blank")

    def post(self): 
        request_data = GIFToVideo.parser.parse_args() # parses through the payload and inserts valid args into request_data
        request_data = request.get_json() # parses through the payload and inserts valid args into request_data

        print(request.get_json(), "\n")


        fileUrl = str(request_data.get("fileUrl"))
        fileKey = str(request_data.get("fileKey"))
        editType = "gif_to_video"
        timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')
        container = ".mp4"

        localOutputPath = "edits/{timestamp}_{editType}.{container}".format(timestamp=timestamp, editType=editType, container=container)


        if container != "gif":
            abort(400, description="This media is not .gif")
        if not fileUrl:
            abort(400, description="The request is missing a valid url to the uploaded video. Please try uploading the video again.")
 
        fileHeaders = requests.head(fileUrl)
        statusCode = fileHeaders.status_code
        message = fileHeaders.reason
        if statusCode not in [200, 202]:
            abort(400, description="There was a {statusCode} {message} issue accessing the file from {fileUrl}. Please make sure the url is accessable and the file is located there.".format(message=message, statusCode=statusCode, fileUrl=fileUrl))


 
        result = run(["ffmpeg", "-i", fileUrl, "-f", container, "-pix_fmt", "yuv420p", localOutputPath], capture_output=True, text=True, check=True)
        s3uploadResponse = s3client.upload(localOutputPath, fileKey)

        return s3uploadResponse, 201 # 201 indicates an Media has been created


class VideoToGIF(Resource): 
    parser = reqparse.RequestParser() # initialize new object to parse request 

    def post(self): 
        request_data = VideoToGIF.parser.parse_args() # parses through the payload and inserts valid args into request_data
        request_data = request.get_json() # parses through the payload and inserts valid args into request_data
  
        fileUrl = str(request_data.get("fileUrl"))
        fileKey = str(request_data.get("fileKey"))
        fileName = fileUrl.split("/")[-1]
        editType = "video_to_gif"
        timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')
        container = fileName.split(".")[1]

        localOutputPath = "edits/{timestamp}_{editType}.gif".format(timestamp=timestamp, editType=editType, container=container)


        if container == "gif":
            abort(400, description="This media is already a .gif")
        if not fileUrl:
            abort(400, description="The request is missing a valid url reference to the uploaded video. Please try uploading the video again.")
        
        fileHeaders = requests.head(fileUrl)
        statusCode = fileHeaders.status_code
        message = fileHeaders.reason
        if statusCode not in [200, 202]:
            abort(400, description="There was a {statusCode} {message} issue accessing the file from {fileUrl}. Please make sure the url is accessable and the file is located there.".format(message=message, statusCode=statusCode, watermarkUrl=fileUrl))

 

        result = run(["ffmpeg", "-i", fileUrl, "-f", "gif", localOutputPath], capture_output=True, text=True, check=True)
        s3uploadResponse = s3client.upload(localOutputPath, fileKey)



        return s3uploadResponse, 201 # 201 indicates an Media has been created
    
    
class VideoTrim(Resource): 
    parser = reqparse.RequestParser() # initialize new object to parse request 
    # parser.add_argument('start', required=True, help="This field can't be blank")
    # parser.add_argument('end', required=True, help="This field can't be blank")
    # parser.add_argument('fileUrl', required=True, help="This field can't be blank")
    # parser.add_argument('fileKey', required=True, help="This field can't be blank")
    # parser.add_argument('fileName', required=True, help="This field can't be blank")


    def post(self): 
        # request_data = VideoTrim.parser.parse_args() # parses through the payload and inserts valid args into request_data
        request_data = request.get_json() # parses through the payload and inserts valid args into request_data


        print(request.get_json(), "\n")

  
        fileUrl = str(request_data.get("fileUrl"))
        fileKey = str(request_data.get("fileKey"))
        fileName = fileUrl.split("/")[-1]
        start = str(request_data.get("start")) # HH:MM:SS
        end = str(request_data.get("end")) # HH:MM:SS
        editType = "trimmed_video"
        timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')
        container = fileName.split(".")[1]


        localOutputPath = "edits/{timestamp}_{editType}.{container}".format(timestamp=timestamp, editType=editType, container=container)


        if (not fileUrl):
            abort(400, description="The request is missing a valid url reference to the uploaded video. Please try uploading the video again.")
        if (not start):
            abort(400, description="The request is missing a start time.")
        if (not end):
            abort(400, description="The request is missing an end time.")

        try:
            startInSeconds = time.get_sec(start)
            endInSeconds = time.get_sec(end)
            print(startInSeconds)
            print(endInSeconds)
            if (startInSeconds > endInSeconds) or (startInSeconds < 0):
                abort(400, description="Please make sure your start time is greater than or equal to 00:00:00, in HH:MM:SS format, and is before your desired end time.")
            if (startInSeconds > endInSeconds):
                abort(400, description="Please make sure your end time is in HH:MM:SS format and is after your desired start time.")

        except ValueError:
            abort(400, description = "Please make sure your input time is in HH:MM:SS format.")      
                
        fileHeaders = requests.head(fileUrl)
        statusCode = fileHeaders.status_code
        message = fileHeaders.reason
        if statusCode not in [200, 202]:
            abort(400, description="There was a {statusCode} {message} issue accessing the file from {fileUrl}. Please make sure the url is accessable and the file is located there.".format(message=message, statusCode=statusCode, fileUrl=fileUrl))



        result = run(["ffmpeg", "-ss", start, "-to", end, "-i", fileUrl, "-c", "copy", localOutputPath], capture_output=True, text=True, check=True)

        s3uploadResponse = s3client.upload(localOutputPath, fileKey)

        return s3uploadResponse, 201 # 201 indicates an Media has been created

class Watermark(Resource): 
    parser = reqparse.RequestParser() # initialize new object to parse request 

    def post(self): 
        request_data = Watermark.parser.parse_args() # parses through the payload and inserts valid args into request_data
        request_data = request.get_json() # parses through the payload and inserts valid args into request_data



        print("Watermark ",request.get_json(), "\n")
  
        fileUrl = str(request_data.get("fileUrl"))
        fileKey = str(request_data.get("fileKey"))
        watermarkUrl = str(request_data.get("watermarkUrl"))
        watermarkTransparency = int(request_data.get("watermarkTransparency"))
        watermarkLocation = str(request_data.get("watermarkLocation"))
        watermarkTransparency = str(watermarkTransparency/100)
        defaultScale = "0.1"

        fileName = fileUrl.split("/")[-1]


        container = fileName.split(".")[1].lower()
        editType = "watermarked_video"
        timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')



        localOutputPath = "edits/{timestamp}_{editType}.{container}".format(timestamp=timestamp, editType=editType, container=container)




        overlay = "overlay=main_w-overlay_w-5:main_h-overlay_h-5" # bottom right
        transparency = "[1]format=rgba,colorchannelmixer=aa={watermarkTransparency}[logo];[0][logo]{overlay}:format=auto,format=yuv420p"

        if not fileUrl:
            abort(400, description="The request is missing a valid url reference to the uploaded video. Please try uploading the video again.")
        if not watermarkUrl:
            abort(400, description="The request is missing a valid url reference to the watermark image.")

        
        watermarkHeaders = requests.head(watermarkUrl)
        statusCode = watermarkHeaders.status_code
        message = watermarkHeaders.reason
        if watermarkHeaders.status_code not in [200, 202]:
            abort(400, description="There was a {statusCode} {message} issue accessing the watermark from {watermarkUrl}. Please make sure the watermark url is accessable and the file is located there.".format(message=message, statusCode=statusCode, watermarkUrl=watermarkUrl))

        if watermarkLocation == "Centered":
            overlay = "overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2"
            transparency = transparency.format(watermarkTransparency=watermarkTransparency, overlay=overlay)

        if watermarkLocation == "Top Left":
            overlay = "overlay=5:5"
            transparency = transparency.format(watermarkTransparency=watermarkTransparency, overlay=overlay)

        if watermarkLocation == "Top Right":
            overlay = "overlay=main_w-overlay_w-5:5"
            transparency = transparency.format(watermarkTransparency=watermarkTransparency, overlay=overlay)

        if watermarkLocation == "Bottom Right":
            overlay = "overlay=main_w-overlay_w-5:main_h-overlay_h-5"
            transparency = transparency.format(watermarkTransparency=watermarkTransparency, overlay=overlay)

        if watermarkLocation == "Bottom Left":
            overlay = "overlay=5:main_h-overlay_h"
            transparency = transparency.format(watermarkTransparency=watermarkTransparency, overlay=overlay)
        

        

        result = run(["ffmpeg", "-i", fileUrl, "-i", watermarkUrl, "-filter_complex", transparency, "-codec:a", "copy", localOutputPath], capture_output=True, text=True, check=True)
        s3uploadResponse = s3client.upload(localOutputPath, fileKey)



        return s3uploadResponse, 201 # 201 indicates a media has been created
    

class RemoveAudio(Resource): 
    parser = reqparse.RequestParser() # initialize new object to parse request 

    def post(self): 
        request_data = RemoveAudio.parser.parse_args() # parses through the payload and inserts valid args into request_data
        request_data = request.get_json() # parses through the payload and inserts valid args into request_data
  
        fileUrl = str(request_data.get("fileUrl"))
        fileKey = str(request_data.get("fileKey"))
        fileName = fileUrl.split("/")[-1]

        container = fileName.split(".")[1].lower()
        editType = "video_without_audio"
        timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')



        localOutputPath = "edits/{timestamp}_{editType}.{container}".format(timestamp=timestamp, editType=editType, container=container)


        # validate file url
        if not fileUrl:
            abort(400, description="The request is missing a valid url reference to the uploaded video. Please try uploading the video again.")
        
        fileHeaders = requests.head(fileUrl)
        statusCode = fileHeaders.status_code
        message = fileHeaders.reason
        if fileHeaders.status_code not in [200, 202]:
            abort(400, description="There was a {statusCode} {message} issue accessing the watermark from {fileUrl}. Please make sure the watermark url is accessable and the file is located there.".format(message=message, statusCode=statusCode, fileUrl=fileUrl))


        result = run(["ffmpeg", "-i", fileUrl, "-c",  "copy", "-an", localOutputPath], capture_output=True, text=True, check=True)



        s3uploadResponse = s3client.upload(localOutputPath, fileKey)


        return s3uploadResponse, 201 # 201 indicates a media has been created
    

class ExtractAudio(Resource): 
    parser = reqparse.RequestParser() # initialize new object to parse request 

    def post(self): 
        request_data = ExtractAudio.parser.parse_args() # parses through the payload and inserts valid args into request_data
        request_data = request.get_json() # parses through the payload and inserts valid args into request_data


        print("ExtractAudio",request.get_json(), "\n")
  
        fileUrl = str(request_data.get("fileUrl"))
        fileKey = str(request_data.get("fileKey"))
        fileName = fileUrl.split("/")[-1]

        container = fileName.split(".")[1].lower()
        editType = "audio_only"
        timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')



        localOutputPath = "edits/{timestamp}_{editType}.{container}".format(timestamp=timestamp, editType=editType, container=container)

        # validate file url
        if not fileUrl:
            abort(400, description="The request is missing a valid url reference to the uploaded video. Please try uploading the video again.")
        
        fileHeaders = requests.head(fileUrl)
        statusCode = fileHeaders.status_code
        message = fileHeaders.reason
        if fileHeaders.status_code not in [200, 202]:
            abort(400, description="There was a {statusCode} {message} issue accessing the watermark from {fileUrl}. Please make sure the watermark url is accessable and the file is located there.".format(message=message, statusCode=statusCode, fileUrl=fileUrl))

  
        result = run(["ffmpeg", "-i", fileUrl, "-vn",  "-y", localOutputPath], capture_output=True, text=True, check=True)

        s3uploadResponse = s3client.upload(localOutputPath, fileKey)


        return s3uploadResponse, 201 # 201 indicates a media has been created
    

class AddText(Resource): 
    parser = reqparse.RequestParser() # initialize new object to parse request 
    parser.add_argument('text', required=True, help="This field can't be blank")
    def post(self): 
        request_data = AddText.parser.parse_args() # parses through the payload and inserts valid args into request_data

        text = request_data.get("text")
        listOfText = text.split(' ')
        print(listOfText)
        ffprobe = run(["ffprobe", "-v", "quiet", "-of", "json",  "-show_streams", "-show_format", "gif_output.gif" ],capture_output=True, text=True, check=True)
        print(ffprobe.stdout)
        sourceFileAnalysis = ffprobe.stdout
        # width = sourceAnalysis.get("width")
        # height = sourceAnalysis.get("width")
        # duration = sourceAnalysis.get("duration")


        result = run(["ffmpeg", "-i", "gif_output.gif", "-vf",  "drawtext=text={text}:x=0:y=1000:fontsize=90:fontcolor=black".format(text=text), "-c:a", "copy", "text_gif_output.gif"], capture_output=True, text=True, check=True)

        print(result.stdout)
        print(result.stderr)
        return {"message" : "Success"}, 201 # 201 indicates an Media has been created
