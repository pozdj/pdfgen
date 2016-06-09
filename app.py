import boto3, json, time
from mail import send_email
from uuid import uuid4
from creator import create

s3 = boto3.resource('s3')
def upload_s3(source_file, filename):
  bucket_name = '167985-last'
  destination_filename = "albums/%s/%s" % (uuid4().hex, filename)
  print destination_filename
  bucket = s3.Bucket(bucket_name)
  bucket.put_object(Key=destination_filename, Body=source_file, ACL='public-read')
  return destination_filename

sqs = boto3.resource('sqs')
albumRequests = sqs.get_queue_by_name(QueueName='last-album')
bucket_address = 'https://s3.eu-central-1.amazonaws.com/167985-last'

while True:
  for albumRequest in albumRequests.receive_messages():
    print('processing request ..........')
    albumData = json.loads(albumRequest.body)
    pdf = create(albumData)
    dest = upload_s3(pdf.getvalue(), 'album.pdf')
    send_email(albumData['sent_to'], 'Your album', 'Your album is ready. <a href="%s/%s">DOWNLOAD HERE</a>' % (
    bucket_address, dest))
    albumRequest.delete()
    print('request processing finished [X]')
  time.sleep(1)
