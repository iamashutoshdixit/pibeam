# python imports
import logging
from datetime import datetime

# django imports
from django.db.models.signals import post_save
from django.dispatch import receiver

# app imports
from .models import (
    Vehicle, 
    Station,
)

logger = logging.getLogger(__name__)


