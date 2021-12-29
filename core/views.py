from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from . import serializers
from core.models import Inquiry, Device
from rest_framework import generics, status
from rest_framework.views import APIView
import json
import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination
from django.utils import timezone

class LargeResultsSetPagination(pagination.PageNumberPagination):
    """
        pagination class
    """
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 10000


api_link = {
    'Hamrahavval':'https://core.inquiry.ayantech.ir/webservices/core.svc/MCIMobileBillInquiry',
    'Irancell':'https://core.inquiry.ayantech.ir/webservices/core.svc/MtnMobileBillInquiry',
    'Rightel':'https://core.inquiry.ayantech.ir/webservices/core.svc/RightelMobileBillInquiry',
    'FixedLine':'https://core.inquiry.ayantech.ir/webservices/core.svc/FixedLineBillInquiry',
    'car':'https://core.inquiry.ayantech.ir/webservices/core.svc/TrafficFinesInquiry',
    'ElectricityBill':'https://core.inquiry.ayantech.ir/webservices/core.svc/ElectricityBillInquiry',
    'GasBill':'https://core.inquiry.ayantech.ir/webservices/core.svc/GasBillInquiry',
    'WaterBill':'https://core.inquiry.ayantech.ir/webservices/core.svc/WaterBillInquiry',
}

def get_data(device):
    """
        the data( that the client intends to inquiry about ) that api received varies according to the device
        so this function give usthe address based on the advice
    """
    device_type = device.device_type

    if device_type == 'Irancell' or device_type == 'Hamrahavval' or device_type == 'Rightel':
        return json.dumps({
                "Identity": {
                    "Token": "3074B060C52E440BABC2BAAA4FF9A8E5"
                    # "Token": "DB5529C5350449C8A71A87ACD6259172"
                },
                "Parameters": {
                    "MobileNumber": device.MobileNumber
                }
            })

    elif device_type == 'FixedLine':
        return json.dumps({
                "Identity": {
                    "Token": "3074B060C52E440BABC2BAAA4FF9A8E5"
                },
                "Parameters": {
                    "FixedLineNumber": device.FixedLineNumber
                }
            })

    elif device_type == 'car':
        return json.dumps({
                "Identity": {
                    "Token": "3074B060C52E440BABC2BAAA4FF9A8E5"
                },
                "Parameters": {
                    "BarCode": device.BarCode
                }
            })
    
    elif device_type == 'ElectricityBill':
        return json.dumps({
                "Identity": {
                    "Token": "3074B060C52E440BABC2BAAA4FF9A8E5"
                },
                "Parameters": {
                    "ElectricityBillID": device.ElectricityBillID
                }
            })
    
    elif device_type == 'GasBill':
        return json.dumps({
                "Identity": {
                    "Token": "3074B060C52E440BABC2BAAA4FF9A8E5"
                },
                "Parameters": {
                    "ParticipateCode": device.ParticipateCode,
                    "GasBillID": device.GasBillID
                }
            })
    
    elif device_type == 'WaterBill':
        return json.dumps({
                "Identity": {
                    "Token": "3074B060C52E440BABC2BAAA4FF9A8E5"
                },
                "Parameters": {
                    "WaterBillID": device.WaterBillID
                }
            })

def change_mapping_data(device, data_dict):
    data_dict.update(data_dict.pop('Description', {}))
    data_dict.update(data_dict.pop('Status', {}))
    data_dict['device'] = device.id
    if not data_dict['Parameters'] == None:
        data_dict.update(data_dict.pop('Parameters', {}))
        if 'FinalTerm' in data_dict.keys():
            if not data_dict['FinalTerm'] == None:
                FinalTerm_data = {"FinalTerm_" + str(key): val for key, val in data_dict['FinalTerm'].items()}
                data_dict.pop('FinalTerm')
                data_dict.update(FinalTerm_data)
            else:
                data_dict.pop('FinalTerm')
        if 'MidTerm' in data_dict.keys():
            if not data_dict['MidTerm'] == None:
                MidTerm_data = {"MidTerm_" + str(key): val for key, val in data_dict['MidTerm'].items()}
                data_dict.pop('MidTerm')
                data_dict.update(MidTerm_data)
            else:
                data_dict.pop('MidTerm')
            
    else:
        data_dict.pop('Parameters')
    
    return data_dict


class BillInquiryApi(APIView):
    """
        create new inquiry for one of the client device
    """

    serializer_class = serializers.BillInquirySerializer

    def post(self, request, *args, **kwargs):
        # serializer = self.serializer_class(data=request.data)
        # serializer = self.serializer_class(data=request.query_params)
        serializer = self.serializer_class(data=kwargs)

        if serializer.is_valid():

            header = {
                'Content-Type':'application/json',
                'Accept':'application/json',
                'Connection':'keep-alive',
                'User-Agent': 'PostmanRuntime/7.28.4',
                'Accept-Encoding':'gzip, deflate, br'
            }
            device = get_object_or_404(Device, pk=int(serializer.data['device']))
            data = get_data( device )
            response = requests.post(
                api_link[device.device_type],
                headers=header,
                data=data,
            )
            responsed_data = response.json()
            maped_data = change_mapping_data(device, responsed_data)

            if maped_data['Code'] == 'G00000':
                s = serializers.BillInquirySerializer(data=maped_data)
                if s.is_valid():
                    s.save()
                    device.last_inquiry = timezone.now()
                    device.save()
                else:
                    s.errors


            return Response(maped_data)
        
        else:
            return Response(
                serializer.errors,

                status=status.HTTP_400_BAD_REQUEST,)


class DeleteDevice(generics.DestroyAPIView):
    """
        Delete Device 
    """
    serializer_class = serializers.DeviceSerializer
    queryset = Device.objects.all()

    def get_object(self, queryset=None):
        # device = Device.objects.get(pk=self.request.query_params['id'])
        device = Device.objects.get(pk=self.kwargs['pk'])
        return device

    def get(self, request, *args, **kwargs):
        device = self.get_object()
        device.delete()
        return Response("Inquiry deleted", status=status.HTTP_204_NO_CONTENT)


class UpdateDevice(generics.UpdateAPIView):
    """
        Update the Device 
    """
    serializer_class = serializers.DeviceSerializer
    queryset = Device.objects.all()

    def get_object(self, queryset=None):
        # device = Device.objects.get(pk=self.request.query_params['id'])
        device = Device.objects.get(pk=self.kwargs['pk'])
        return device

    def post(self, request, *args, **kwargs):
        device = self.get_object()
        serializer = serializers.DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            device = serializer.save()
            return Response(serializers.DeviceSerializer(device).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateDevice(generics.CreateAPIView):
    """
        Create the Device 
    """
    serializer_class = serializers.DeviceSerializer

    def create(self,request, *args, **kwargs):
        self.request.data['created_by'] = 1
        return super(CreateDevice, self).create(request, *args, **kwargs)

    # def perform_create(self, serializer):
    #     serializer.save(created_by=1)


class ListDevice(generics.ListAPIView):
    """
        Retrieve Devices
    """
    queryset = Device.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner', 'device_type', 'is_active',]
    ordering_fields = ['owner', 'device_type', 'is_active']
    serializer_class = serializers.DeviceSerializer
    pagination_class = LargeResultsSetPagination
    page_size = 2
    page_size_query_param = 'page_size'
    

class ListInquiry(generics.ListAPIView):
    """
        Retrieve inquiries
    """
    queryset = Inquiry.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device',]
    ordering_fields = ['device',]
    serializer_class = serializers.BillInquirySerializer
    pagination_class = LargeResultsSetPagination
    page_size = 2
    page_size_query_param = 'page_size'

