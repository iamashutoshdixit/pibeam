from main.celery import app
from django.core.cache import cache
from time import sleep
import logging

logger = logging.getLogger("drivers.views")


@app.task(name="print_hello")
def print_hello():
    cache.set("hello", "world", timeout=3600)
    logging.info("msg")
    sleep(10)
    print("hello world")
