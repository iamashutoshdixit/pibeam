TRIP_START_TIME_DELTA = 120
TRIP_END_TIME_DELTA = 120

VEHICLE_ID_MISSING = {
    "code": "FLT_400",
    "error": "vehicle id missing",
}

VEHICLE_NOT_FOUND = {
    "code": "FLT_404",
    "error": "vehicle with given id not found or inactive",
}

VEHICLE_INACTIVE = {
    "code": "FLT_405",
    "error": "vehicle with given id is inactive",
}

ROSTER_TRIP_COMPLETED_ALREADY = {
    "code": "FLT_500",
    "error": "you have already finished the roster for today."
}

PREVIOUS_TRIP_ACTIVE = {
    "code": "FLT_501",
    "error": "previous trip not ended."
}

TRIP_CANNOT_START = {
    "code": "FLT_502",
    "error": "you cannot start roster now."
}

ROSTER_NOT_ASSIGNED = {
    "code": "FLT_503",
    "error": "you are not assigned to this roster"
}
