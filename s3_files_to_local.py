import os
import boto3
import sys
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import csv


def Create_Presigned_Url(bucket_key,expire_time=3600):

	S3_client = boto3.client("s3", aws_access_key_id='AKIAXFTFOMDPL7I74EWX',aws_secret_access_key='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',region_name='ap-south-1')

	try:

		Response = S3_client.generate_presigned_url('get_object',
				                                    Params={'Bucket': 'rufilo-application-bucket-prod',
				                                            'Key': bucket_key},
				                                    ExpiresIn=expire_time)

		return Response

	except ClientError as e:

		return False

Dir_Save = input("Enter Directory Name - ")
File_Name = input("Enter the File Name - ")

try:
    os.stat(Dir_Save)
except:
    os.mkdir(Dir_Save)

with open(File_Name, 'r') as file:
	reader = csv.reader(file)

	for row in reader:

		if not row[0] == 'document_url':

			get_file_name = row[0].split('/')

			Presigned_url = Create_Presigned_Url(row[0])

			response = urllib2.urlopen(Presigned_url)
			zipcontent= response.read()

			with open(Dir_Save+'/'+get_file_name[-1], 'wb') as f:
				f.write(zipcontent)
