from boto3 import resource


def get_csv_from_s3(bucket_name, upload_id):
    s3 = resource('s3')
    file_name = '{}.csv'.format(upload_id)
    key = s3.Object(bucket_name, file_name)
    contents = key.get()['Body'].read().decode('utf-8')
    return contents
