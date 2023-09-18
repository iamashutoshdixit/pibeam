# Python imports
import logging
import datetime as dt
from datetime import datetime


# Django imports
from django.core.exceptions import ValidationError

# project level imports
from fleets.models import Vehicle, Station

# app level imports

logger = logging.getLogger(__name__)


def driver_age_validator(date):
    """
    Validation for the driver age
    """
    today = dt.date.today()
    age = (today - date).days / 365.24
    if age < 18:
        raise ValidationError("Minimum age for driver is 18 years")
    return date
