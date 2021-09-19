# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3
import io
import os
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont

# os.environ['AWS_PROFILE'] = "Profile1"
# os.environ['AWS_DEFAULT_REGION'] = "us-west-2"

# os.environ['AWS_PROFILE'] = "default"
# os.environ['AWS_DEFAULT_REGION'] = "us-west-2"

def show_custom_labels(model, bucket, photo, min_confidence):
    client = boto3.client('rekognition',
                          region_name="us-east-1",
                          aws_access_key_id="AKIAIMPLMZRICBK5I6SQ",
                          aws_secret_access_key="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"
    )

    # Load image from S3 bucket
    s3_connection = boto3.resource('s3',
                                   aws_access_key_id = "AKIAXQ4CJILWH7FRBW4A",
                                   aws_secret_access_key = "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",
                                   region_name="us-east-1",
                                   )

    s3_object = s3_connection.Object(bucket, photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)

    # Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object':
                                                  {'Bucket': bucket,
                                                   'Name': photo}},
                                           MinConfidence=min_confidence,
                                           ProjectVersionArn=model)

    print(response)
    # imgWidth, imgHeight = image.size
    # draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    # print('Detected custom labels for ' + photo)
    # for customLabel in response['CustomLabels']:
    #     print('Label ' + str(customLabel['Name']))
    #     print('Confidence ' + str(customLabel['Confidence']))
    #     if 'Geometry' in customLabel:
    #         box = customLabel['Geometry']['BoundingBox']
    #         left = imgWidth * box['Left']
    #         top = imgHeight * box['Top']
    #         width = imgWidth * box['Width']
    #         height = imgHeight * box['Height']
    #
    #         fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
    #         draw.text((left, top), customLabel['Name'], fill='#00d400', font=fnt)
    #
    #         print('Left: ' + '{0:.0f}'.format(left))
    #         print('Top: ' + '{0:.0f}'.format(top))
    #         print('Label Width: ' + "{0:.0f}".format(width))
    #         print('Label Height: ' + "{0:.0f}".format(height))
    #
    #         points = (
    #             (left, top),
    #             (left + width, top),
    #             (left + width, top + height),
    #             (left, top + height),
    #             (left, top))
    #         draw.line(points, fill='#00d400', width=5)
    #
    # image.show()

    return len(response['CustomLabels'])


def main():
    bucket = "aadhardata"
    photo = "LOS1358146327589H2CG_POA_CROP.jpg"
    model = "arn:aws:rekognition:us-east-1:517279924972:project/Custom-Label/version/Custom-Label.2020-12-11T19.27.11/1607695031912"
    min_confidence = 80
    region_name = 'us-east-1'

    label_count = show_custom_labels(model, bucket, photo, min_confidence)
    print("Custom labels detected: " + str(label_count))


if __name__ == "__main__":
    main()