import boto3 
import botocore 
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")

class S3Client:
    def __init__(self):
        self.bucket_name = config.get("bucket_name")
        self.region_name = config.get("regiont_name")
        self.s3_base_uri = config.get("s3_base_uri")
        self.s3 = boto3.resource('s3', aws_access_key_id=config.get("aws_access_key_id"),
        aws_secret_access_key=config.get("aws_secret_access_key"))

    def upload(self, ffmpegOutputPath: str, fileKey: str):
        try:
            with open(ffmpegOutputPath, 'rb') as data:
                originalUploadKey = fileKey.split("/")[0] + "/"
                self.s3.Bucket(self.bucket_name).put_object(Key=originalUploadKey+ffmpegOutputPath, Body=data)

                fileName = (self.s3_base_uri+originalUploadKey+ffmpegOutputPath).split("/")[5]
                fileExtension = fileName.split(".")[1]
            return {"fileUrl" : self.s3_base_uri+originalUploadKey+ffmpegOutputPath, "fileName":fileName, "fileExtension":fileExtension}
        
        except botocore.exceptions.ClientError as e:
            print(e.response['Error'])
            errorCode = e.response['Error']['Code']
            if errorCode == "400":
                return {"message" : "Bad Request {errorCode}".format(errorCode=errorCode)}
            if errorCode == "404":
                return {"message" : "File not found {errorCode}".format(errorCode=errorCode)}
            if errorCode == "403":
                return {"message" : "Not Authenticated {errorCode}".format(errorCode=errorCode)}
            if errorCode == "500":
                return {"message" : "Internal Server Error {errorCode}".format(errorCode=errorCode)}
    
