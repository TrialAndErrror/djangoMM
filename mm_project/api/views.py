from django.shortcuts import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Bill, Account, User
from .serializers import BillSerializer, AccountSerializer, UserSerializer


# Create your views here.
# def api_home(request):
#     return HttpResponse("API home")
#
#
# @api_view(['GET'])
# def user_profile(request, user_id):
#     user_obj = User.objects.get(id=user_id)
#     if user_obj:
#         serializer = UserSerializer(user_obj)
#         return Response(serializer.data)
#     return Response({"Error": f"User id {user_id} not found"}, status=404)
#
#
# @api_view(['GET'])
# def all_bills(request):
#     results = Bill.objects.all()
#     serializer = BillSerializer(results, many=True)
#     return Response(serializer.data)
#
#
# @api_view(['GET'])
# def all_user_bills(request, user):
#     results = Bill.objects.filter(owner=user)
#     serializer = BillSerializer(results, many=True)
#     return Response(serializer.data)
#
#
# def one_user_bill(request, user, id):
#     found_bill = Bill.objects.filter(owner=user, id=id)
#     if found_bill:
#         serializer = BillSerializer(found_bill)
#         return Response(serializer.data)
#     return Response({"Error": f"Bill id {id} not found"}, status=404)
#
#
# def one_bill(request, id):
#     found_bill = Bill.objects.get(id=id)
#     if found_bill:
#         serializer = BillSerializer(found_bill)
#         return Response(serializer.data)
#     return Response({"Error": f"Bill id {id} not found"}, status=404)
