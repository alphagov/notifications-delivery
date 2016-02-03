from boto3 import resource


def get_csv_from_s3(service_id, upload_id):
    s3 = resource('s3')
    bucket_name = 'service-{}-notify'.format(service_id)
    key = s3.Object(bucket_name, upload_id)
    contents = key.get()['Body'].read().decode('utf-8')
    return contents
