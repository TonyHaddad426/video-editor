import boto3 
import botocore 
import json 

class timestampToSeconds:
    def __init__(self):
        print("initiailized")

        
    def get_sec(self, time_str):
        """Get seconds from time."""
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)


