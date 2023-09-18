TRIP_START_TIME_DELTA = 120
TRIP_END_TIME_DELTA = 120

TRIP_ENDED_ALREADY = {
    "code": "BKG_500",
    "error": "trip has already ended",
}

TRIP_NOT_FOUND = {
    "code": "BKG_501",
    "error": "trip not found",
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

TRIP_INVALID_ACTION = {
    "code": "FLT_504",
    "error": "the roster action is invalid."
}

TRIP_VEHICLE_NOT_ASSIGNED = {
    "code": "FLT_505",
    "error": "vehicle is not assigned to the roster."
}