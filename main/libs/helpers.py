# python imports
import time
import logging
# django imports
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import boto3

logger = logging.getLogger(__name__)


def csv_dispatcher(content):
    """
    Convert content to csv and send as downlooad
    """
    filename = int(time.time())
    response = HttpResponse(content, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    return response


class S3FileUpload():
    def __init__(self, *args, **kwargs):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_CONFIG["S3"]["AWS_S3_ACCESS_KEY_ID"],
            aws_secret_access_key=settings.AWS_CONFIG["S3"]["AWS_S3_SECRET_ACCESS_KEY"],
        )
        self.s3 = session.resource('s3')

    def get_file_ext(self, file):
        return file.name.split(".")[-1]

    def upload_file(self, file, folder):
        filename = str(int(time.time())) + "." + self.get_file_ext(file)
        region = settings.AWS_CONFIG["S3"]["AWS_S3_REGION_NAME"]
        bucket = settings.AWS_CONFIG["S3"]["AWS_STORAGE_BUCKET_NAME"]
        try:
            self.s3.Bucket(bucket).put_object(Key=folder + filename, Body=file)
            file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{folder}{filename}"
            return True, file_url
        except Exception as e:
            logger.error(e, exc_info=True)
            return False, None


def email(subject, message, recipient_list, email_from=settings.EMAIL_HOST_USER):
    send_mail( subject, message, email_from, recipient_list )