# Python imports
import uuid
import json
import boto3
import requests
import logging
import threading
from botocore.client import Config as Cfg

# Django imports
from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, action

# project imports
from config.models import Config

# app imports
from .models import (
    Onboarding,
    Driver,
    DriverLocations,
    DriverContractLog,
    DriverContract,
    DriverAadharDetails,
)
from .serializers import (
    OnboardingSerializer,
    DriverSerializer,
    DriverLocationsSerializer,
    DriverContractSerializer,
)
from libs.constants import INVALID_DATA

logger = logging.getLogger(__name__)


class OnboardingViewSet(viewsets.ModelViewSet):
    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer
    http_method_names = ["post"]


class DriverLocationsViewSet(viewsets.ModelViewSet):
    queryset = DriverLocations.objects.all()
    serializer_class = DriverLocationsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.filter(is_active=True)
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def list(self, request):
        driver = Driver.objects.filter(user=request.user).first()
        serializer = DriverSerializer(driver)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if request.user.id == pk:
            return Driver.objects.filter(id=pk).first()
        return Response({"Error": "403 Forbidden"})
    
    @action(methods=['POST'], detail=True, url_path='app-version')
    def app_version(self, request, *args, **kwargs):
        driver = self.get_object()
        try:
            driver.app_version = request.data["app_version"]
        except KeyError:
            return Response(
                INVALID_DATA,
                status=status.HTTP_400_BAD_REQUEST,
            )
        driver.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DriverContractViewSet(viewsets.ModelViewSet):
    queryset = DriverContract.objects.all()
    serializer_class = DriverContractSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    # TODO: paginate this
    def retrieve(self, request, pk=None):
        if str(pk) == "-1":
            latest_contract = Config.get_value("latest_contract")
            if latest_contract is None:
                most_recent = DriverContract.objects.all().order_by(
                    "-created_at",
                ).last()
                latest_contract = most_recent.id
                Config.objects.create(
                    key="latest_contract",
                    value=latest_contract,
                )
                contract = most_recent
            else:
                contract = DriverContract.objects.get(id=latest_contract)
            serializer = self.serializer_class(contract)
            return Response(serializer.data)
        else:
            return super().retrieve(request, pk)

    @action(methods=['POST'], detail=False, url_path='accept-contract')
    def accept_contract(self, request, *args, **kwargs):
        driver = Driver.objects.get(id=request.user.id)
        latest_contract = Config.get_value("latest_contract")
        contract = DriverContract.objects.get(id=latest_contract)
        if not driver.contract_accepted:
            driver.contract_accepted = True
            driver.contract = contract
            driver.save()
            DriverContractLog.objects.create(
                driver=driver,
                contract=contract,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetUploadURL(views.APIView):
    def get(self, request):
        # Get the service client.
        session = boto3.Session(
            aws_access_key_id=settings.AWS_CONFIG["S3"]["AWS_S3_ACCESS_KEY_ID"],
            aws_secret_access_key=settings.AWS_CONFIG["S3"]["AWS_S3_SECRET_ACCESS_KEY"],
        )
        s3 = session.client(
            "s3",
            region_name=settings.AWS_CONFIG["S3"]["AWS_S3_REGION_NAME"],
            config=Cfg(signature_version=settings.AWS_CONFIG["S3"]["AWS_S3_SIGNATURE_VERSION"]),
        )
        filename = request.GET.get("key", str(uuid.uuid4()))
        folder = request.GET.get("folder", "")
        url = s3.generate_presigned_post(
            settings.AWS_CONFIG["S3"]["AWS_STORAGE_BUCKET_NAME"], 
            folder + '/' + filename, 
            ExpiresIn=86400,
        )
        return Response(url)


@api_view(["post"])
def send_otp(request):
    token = settings.KYC_TOKEN
    url = f"{settings.KYC_URL}/aadhaar-v2/generate-otp"
    aadhar_number = request.data.get("aadhar_number", None)
    aadhar_details = DriverAadharDetails.objects.filter(
        aadhar_number=aadhar_number
    ).first()
    if aadhar_details:
        data = json.loads(aadhar_details.data)
        cache.set(aadhar_number, {"data": data}, timeout=6000)
        return Response(
            "we already have your details. Please skip this step and proceed.",
        )
    if aadhar_number is None:
        return Response(
            {"aadhar_number": "this field is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    params = {
        "headers": {"Authorization": f"Bearer {token}"},
        "data": {"id_number": aadhar_number},
    }
    res = requests.post(url, **params)
    return Response(res.json())


def submit_aadhar_otp(client_id, otp):
    token = settings.KYC_TOKEN
    url = f"{settings.KYC_URL}/aadhaar-v2/submit-otp"
    params = {
        "headers": {"Authorization": f"Bearer {token}"},
        "data": {"client_id": client_id, "otp": otp},
    }
    res_raw = requests.post(url, **params)
    res = res_raw.json()
    cache.set(res["data"]["aadhaar_number"], res, timeout=6000)


@api_view(["post"])
def submit_otp(request):
    errors = {}
    client_id = request.data.get("client_id", None)
    otp = request.data.get("otp", None)
    if not client_id:
        errors["client_id"] = "this field is required."
    if not otp:
        errors["otp"] = "this field is required."
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    t = threading.Thread(target=submit_aadhar_otp, args=(client_id, otp))
    t.start()
    return Response(status=status.HTTP_204_NO_CONTENT)
