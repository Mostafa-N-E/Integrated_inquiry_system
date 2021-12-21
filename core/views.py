from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from . import serializers
from core.models import Inquiry, Device
from rest_framework import generics, status
from rest_framework.views import APIView
import json
import requests


api_operator_link = {
    'Mobile':{
        'Hamrahavval':'https://core.inquiry.ayantech.ir/webservices/core.svc/MCIMobileBillInquiry',
        'Irancell':'https://core.inquiry.ayantech.ir/webservices/core.svc/MCIExtendedBillInquiryRequestOtp',
        'Rightel':'https://core.inquiry.ayantech.ir/webservices/core.svc/RightelMobileBillInquiry',
    },
    'FixedLine':'https://core.inquiry.ayantech.ir/webservices/core.svc/FixedLineBillInquiry'
}

# def merge_two_dicts(x, y):
#     z = x.copy()   
#     z.update(y)    
#     return z

def determine_device(device_ID):
    device = get_object_or_404(Device, pk=int(device_ID))
    return device
    
def get_data(device):
    device_type = device.device_type

    if device_type == 'phone':
        print(device.Number)
        return {
                "Identity": {
                    # "Token": "3074B060C52E440BABC2BAAA4FF9A8E5"
                    "Token": "DB5529C5350449C8A71A87ACD6259172"
                },
                "Parameters": {
                    "MobileNumber": device.Number
                }
            }
    elif device_type == 'car':
        return {
                "Identity": {
                    "Token": "3074B060C52E440BABC2BAAA4FF9A8E5"
                },
                "Parameters": {
                    "MobileNumber": device.BarCode
                }
            }
def change_mapping_data(device, data_dict):
    data_dict.update(data_dict.pop('Description', {}))
    data_dict.update(data_dict.pop('Status', {}))

    if not data_dict['Parameters'] == None:
        data_dict.update(data_dict.pop('Parameters', {}))
        if not data_dict['FinalTerm'] == None:
            FinalTerm_data = {"FinalTerm_" + str(key): val for key, val in data_dict['FinalTerm'].items()}
            data_dict.pop('FinalTerm')
            data_dict.update(FinalTerm_data)
        else:
            data_dict.pop('FinalTerm')

        if not data_dict['MidTerm'] == None:
            MidTerm_data = {"MidTerm_" + str(key): val for key, val in data_dict['MidTerm'].items()}
            data_dict.pop('MidTerm')
            data_dict.update(MidTerm_data)
        else:
            data_dict.pop('MidTerm')
            
    else:
        data_dict.pop('Parameters')
    
    return data_dict


def get_api_operator_link(device):
    device_type = device.device_type

    if device_type == 'phone':
        if api_operator_link[device.TypeLine] == 'Mobile':
            return api_operator_link[device.TypeLine][device.Operator]
        else:
            return api_operator_link[device.TypeLine]


class BillInquiryApi(APIView):
    serializer_class = serializers.BillInquirySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            header = {
                'Content-Type':'application/json',
                'Accept':'application/json',
                'Connection':'keep-alive',
                'User-Agent': 'PostmanRuntime/7.28.4',
                'Accept-Encoding':'gzip, deflate, br'
            }
            device = determine_device( serializer.data['device_id'] )
            data = get_data( device )
            api_link = get_api_operator_link( device )
            print(api_link)
            response = requests.post(
                api_link,
                headers=header,
                data=json.dumps(data)
                # data=data
            )
            data_dict = response.json()
            print(data_dict)
            data_dict = change_mapping_data(device,data_dict)
            print(data_dict)
            # data_res = merge_two_dicts( device_data ,data_dict)
            # print(data_res)

            if data_dict['Code'] == 'G00000':
                m = Inquiry(**data_dict)
                m.device = device
                m.save()

            return Response({'message': data_dict['Description']})
        
        else:
            return Response(
                serializer.errors,

                status=status.HTTP_400_BAD_REQUEST,)


# class InquiryDetail(generics.RetrieveUpdateDestroyAPIView):
#
#     def retrieve(self, request, *args, **kwargs):
#         phone = get_object_or_404(Phone, pk=kwargs.get('pk'))
#         serializer = serializers.PhoneSerializer(phone)
#         return Response(serializer.data)
#
#     def destroy(self, request, *args, **kwargs):
#         question = get_object_or_404(Phone, pk=kwargs.get('pk'))
#         question.delete()
#         return Response("Inquiry deleted", status=status.HTTP_204_NO_CONTENT)
#
#     def update(self, request, *args, **kwargs):
#         phone = get_object_or_404(Phone, pk=kwargs.get('pk'))
#         serializer = serializers.PhoneSerializer(phone, data=request.data, partial=True)
#         if serializer.is_valid():
#             phone = serializer.save()
#             return Response(serializers.PhoneSerializer(phone).data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteInquiry(generics.RetrieveAPIView):
    queryset = Device.objects.all()

    def get(self, request, *args, **kwargs):
        question = get_object_or_404(Phone, pk=kwargs.get('pk'))
        question.delete()
        return Response("Inquiry deleted", status=status.HTTP_204_NO_CONTENT)


class UpdateInquiry(generics.UpdateAPIView):
    queryset = Device.objects.all()

    def get(self, request, *args, **kwargs):
        phone = get_object_or_404(Phone, pk=kwargs.get('pk'))
        serializer = serializers.DeviceSerializer(phone, data=request.data, partial=True)
        if serializer.is_valid():
            phone = serializer.save()
            return Response(serializers.PhoneSerializer(phone).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveDevice(generics.UpdateAPIView):
    queryset = Device.objects.all()

    def get(self, request, *args, **kwargs):
        devices = Device.objects.filter(is_active = True)
        serializer = serializers.DeviceSerializer(devices,  many=True)
        return Response(serializer.data)



    # def get_serializer_class(self):
    #     print("******************************************##########")
    #     if self.request.method == 'POST':
    #         print("******************************************")
    #         print(self.request.data)
    #         type_line = self.request.data['TypeLine']
    #
    #         if type_line == 'Mobile':
    #             operator = self.request.data['Operator']
    #             if operator == 'Irancell':
    #                 print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    #                 return serializers.IrancelMobileBillInquirySerializer
    #             elif operator == 'Hamrahavval':
    #                 return serializers.MtnMobileBillInquirySerializer
    #             elif operator == 'Rightel':
    #                 return serializers.MtnMobileBillInquirySerializer
    #             else:
    #                 return serializers.MobileBillInquirySerializer
    #
    #         else:
    #             return serializers.FixedLineBillInquirySerializer
    #
    #     elif self.request.method == 'GET':
    #         return serializers.BillInquirySerializer
    #     else:
    #         return serializers.PhoneBillInquirySerializer

    # def get(self, request, format=None):