## Endpoint: `/drivers/onboardings/`

Onboarding object:

```json
{
    "full_name": string,
    "dob": date,
    "mobile_no": integer,
    "house_no": string,
    "street": string,
    "locality": string,
    "city": string,
    "pincode": integer,
    "state": string,
    "own_house": boolean,
    "photo": url,
    "aadhar_number": integer,
    "aadhar_front": url,
    "aadhar_back": url,
    "pan_number": string (optional),
    "pan_front": url (optional),
    "driver_license_number": string (optional),
    "driver_license_front": url (optional),
    "driver_license_back": url (optional),
    "account_number": integer,
    "account_name": string,
    "ifsc_code": string,
}
```

#### POST

Create a new onboarding

- Request Params:
  None
- Headers:
  ```
  Content-Type: appication/json
  ```
- Request Body:
  ```json
  {
    "full_name": string,
    "dob": date,
    "mobile_no": integer,
    "house_no": string,
    "street": string,
    "locality": string,
    "city": string,
    "pincode": integer,
    "state": string,
    "own_house": boolean,
    "photo": url,
    "aadhar_number": integer,
    "aadhar_front": url,
    "aadhar_back": url,
    "pan_number": string (optional),
    "pan_front": url (optional),
    "driver_license_number": string (optional),
    "driver_license_front": url (optional),
    "driver_license_back": url (optional),
    "account_number": integer,
    "account_name": string,
    "ifsc_code": string,
  }
  ```
- Response:
  ```json
  { <new-onboarding-object-created> }
  ```

## Endpoint: `/drivers/onboardings/:id/`

#### GET

Get onboarding details for the given id

- Request params:
  `id`: required
- Headers:
  Authorization: Token \<token\>
- Response:
  ```json
  { <onboarding-object> }
  ```

## Endpoint `/users/login/`

#### POST

Get the auth token for authorizing users

- Request Params:
  None
- Headers:
  ```json
  {
      "Content-Type": application/json
  }
  ```
- Request Body:
  ```json
  {
      "username": string,
      "password": string
  }
  ```
- Response:
  ```json
  {
    "token": string,
    "user_id": integer,
    "username": string
  }
  ```
- Errors:
  - User inactive or incorrent credentials:
    ```json
    {
      "code": "USR_404",
      "error": "User not found or incorrect credentials."
    }
    ```

## Endpoint `/drivers/s3-upload?key=:name`

### GET

Get a pre-signed url to upload a file to s3

- Request Params:
  name: (optional) filename for the file in bucket
- Response:
  ```json
  {
    "url": url,
    "fields": {
      "key": string,
      "x-amz-algorithm": string,
      "x-amz-credential": string,
      "x-amz-date": string,
      "policy": string,
      "x-amz-signature": string
    }
  }
  ```

## Endpoint `/drivers/trips/`

Trip object:

```json
{
    "id": integer,
    "driver": integer,
    "vehicle": integer,
    "roster": integer,
    "checkin_time": datetime,
    "checkout_time": datetime,
    "in_latitude": float,
    "in_longitude": float,
    "out_latitude": float,
    "out_longitude": float,
    "created_at": datetime,
    "ended_at": datetime,
    "start_km": integer,
    "end_km": integer
}
```

#### GET

Get all trip records for current user

- Request Params:
  None
- Headers:
  ```json
  {
      "Content-Type": application/json,
      "Authorization": Token <token>
  }
  ```
- Request Body:
  None
- Response:
  ```json
  [
    { <trip-object1> },
    { <trip-object2> },
    { <trip-object3> },
    { <trip-object4> },
  ]
  ```
- Errors:

#### POST

- Request Params:
  None
- Headers:
  ```json
  {
      "Content-Type": application/json,
      "Authorization": Token <token>
  }
  ```
- Request Body:
  ```json
  {
    "driver": integer,
    "vehicle": integer,
    "checkin_time": time,
    "in_latitude": float,
    "in_longitude": float
  }
  ```
- Response:
  ```json
  <newly-created-trip-object>
  ```

## Endpoint `/drivers/roster/`

trip object:

```json
{
    "id": integer,
    "driver": integer,
    "vehicle": integer,
    "start_date": date (ISO String),
    "end_date": date (ISO String),
    "holiday": date (ISO String),
    "slot_start_time": time (ISO String),
    "slot_end_time": time (ISO String),
    "lat": float,
    "long": float,
    "address": string,
}
```

#### GET

Get all active roster records for current driver

- Request Params:
  None
- Headers:
  ```json
  {
      "Content-Type": application/json,
      "Authorization": Token <token>
  }
  ```
- Request Body:
  None
- Response:
  ```json
  [
    { <roster-object1> },
    { <roster-object2> },
    { <roster-object3> },
    { <roster-object4> },
  ]
  ```
- Errors:

## Endpoint `/drivers/trip/:id/`

trip object:

```json
{
  "id": integer,
  "driver": integer,
  "vehicle": integer,
  "checkin_time": time,
  "checkout_time": time,
  "in_latitude": float,
  "in_longitude": float,
  "out_latitude": float,
  "out_longitude": float,
}
```

#### PATCH

Update trip record with selected fields

- Request Params:
  None
- Headers:
  ```json
  {
      "Content-Type": application/json,
      "Authorization": Token <token>
  }
  ```
- Request Body:
  ```json
  {
    "out_latitude": float,
    "out_longitude": float,
  }
  ```
  or
  ```json
  {
    "in_latitude": float,
    "in_longitude": float,
  }
  ```

- Response:
  ```json
  <updated-trip-object>,
  ```
- Errors:

## Endpoint `/drivers/drivers/`

Driver object

```json
{
    "id": integer (driver id),
    "user": integer (user id for the object),
    "details": { Onboarding object },
    "doj": date of joininng,
    "dol": date of leaving,
}
```

#### GET

- Request Params:
  None
- Headers:
  ```json
  {
      "Content-Type": application/json,
      "Authorization": Token <token>
  }
  ```
- Request Body:
  None
- Response:
  ```json
  <driver-object>
  ```

## Endpoint `/fleets/vehicle-available/`

#### POST

Change a vehicle status to available

- Request Params:
- Headers:
  ```json
  {
      "Content-Type": application/json,
      "Authorization": Token <token>
  }
  ```
- Request Body:
  ```json
  {
    "id": integer
  }
  ```
- Response:
  ```json
  {
    "success": "vehicle status updated to available"
  }
  ```
- Errors:
  - Vehicle id missing in request body
    ```json
    {
      "code": "FLT_400",
      "error": "vehicle id missing"
    }
    ```
  - Vehicle with given id not found
    ```json
    {
      "code": "FLT_404",
      "error": "vehicle with given id not found"
    }
    ```

## Endpoint `/fleets/vehicle-booked/`

#### POST

Change a vehicle status to under booking

- Request Params:
  None
- Headers:
  ```json
  {
      "Content-Type": application/json,
      "Authorization": Token <token>
  }
  ```
- Request Body:
  ```json
  {
    "id": integer
  }
  ```
- Response:
  ```json
  {
    "success": "vehicle status updated to under booking"
  }
  ```
- Errors:
  - Vehicle id missing in request body
    ```json
    {
      "code": "FLT_400",
      "error": "vehicle id missing"
    }
    ```
  - Vehicle with given id not found
    ```json
    {
      "code": "FLT_404",
      "error": "vehicle with given id not found"
    }
    ```


## Endpoint `/drivers/contracts/`

Contract object:
```json
    "created_at":datetime,
    "description":string,
    "id": integer,
    "is_active": boolean,
    "name":string,
    "updated_at":datetime,
    "url":url
```

#### GET

Get list of all contracts

Response:
```
[
    {contract-object-1},
    {contract-object-2},
    {contract-object-3},
    ...
]
```

## Endpoint `/drivers/contract/:id/`

#### GET

get driver contract for a particular id (-1 for the latest)

Request params;
id: id of the contract

Response:
```json
{
    "created_at":datetime,
    "description":string,
    "id":integer,
    "is_active": boolean,
    "name":string,
    "updated_at":datetime,
    "url":url
}
```

## Endpoint `/drivers/accept-contract`

#### POST

accept the contract

Request Params: None
Response: None
Status Code: 204

## Endpoint `/fleets/start-ride/`

#### POST

start the ride and get trip details

Request Body:

```json
{
    "roster": integer,
    "start_km": integer
}
```

**Response**

```json
{
    "id": integer,
    "driver": integer,
    "roster":integer,
    "vehicle":integer,
    "checkin_time":datetime,
    "in_latitude":float,
    "in_longitude":float,
    "checkout_time":datetime,
    "out_latitude":float,
    "out_longitude":float,
    "start_km":integer,
    "end_km":integer,
    "created_at":datetime,
    "ended_at": datetime
}
```

## Endpoint `/fleets/end-ride/`

#### POST

end the ride

Request Body:
```json
{
    "trip_id": integer,
    "trip_sheet_photo": url,
    "end_km":
}
```

Response:
```json
{
    "id": integer,
    "driver": integer,
    "roster":integer,
    "vehicle":integer,
    "checkin_time":datetime,
    "in_latitude":float,
    "in_longitude":float,
    "checkout_time":datetime,
    "out_latitude":float,
    "out_longitude":float,
    "start_km":integer,
    "end_km":integer,
    "created_at":datetime,
    "ended_at": datetime
}
```

## Endpoint `/drivers/generate-otp`

### POST

Send otp to mobile number

Request Body:
```json
{
    "aadhar_number": integer
}
```

Response:
```json
{
    "data": {
        "client_id": string,
        "if_number": boolean,
        "otp_sent": boolean,
        "valid_aadhaar": boolean
    },
    "message": string,
    "message_code": string,
    "status_code": integer,
    "success": boolean
}
```


## Endpoint `/drivers/submit-otp`

### POST

Submit otp

requset body:
```json
{
    "client_id": string
    "otp": integer
}
```
