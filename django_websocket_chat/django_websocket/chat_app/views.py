from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.request import Request 
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from rest_framework.response import Response
from .serializers import *
from django.http import JsonResponse
from itertools import groupby
from django.db.models import Q
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework_simplejwt.tokens import RefreshToken

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                "501914681032-tkfjo4a2ossqcq4n7hcccjqrnp96dr0s.apps.googleusercontent.com"
            )

            email = idinfo['email']
            name = idinfo.get('name', '')

            # Get or create the user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email, 'first_name': name}
            )

            if user:
                user_detail_obj = UserDetail.objects.create(
                    user_id = user
                )

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            return Response({
                'refresh': str(refresh),
                'access': str(access),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name,
                }
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class Dashboard(APIView):
    def get(self, request):
        result = False
        message = 'Failure'
        print(request.data)
        try:
            user_id = request.query_params.get('user_id')
            if user_id:
                user_obj = UserDetail.objects.get(user_id__id=user_id)
                serializer = UserDetailsSerializer(user_obj)
            else:    
                user_objs = UserDetail.objects.all()
                print(1111)
                serializer = UserDetailsSerializer(user_objs, many=True)
            result = True
            message = 'Success'
            return JsonResponse({
                "result": result,
                "message": message,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserCreation(APIView):
    parser_classes = [MultiPartParser, FormParser]  

    def post(self, request):
        try:
            data = request.data
            print(request.data)

            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                print("Serializer is valid")
                print(2222222)
                user_obj = serializer.save()
                user_obj.set_password(data['password'])
                user_obj.save()

                user_detail_obj = UserDetail()
                user_detail_obj.user_id = user_obj
                user_detail_obj.gender = data.get('gender')
                user_detail_obj.dob = data.get('dob')
                user_detail_obj.profile_pic = data.get('profile_pic')
                user_detail_obj.save()

                return Response({"message":"user created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            user_detail_list = []
            user_id = request.GET.get('user_id')
            print(user_id)

            if user_id:
                user_detail_obj = UserDetail.objects.filter(user_id__id=user_id).first()
                if user_detail_obj:
                    user_detail_dict = {
                        'id' : user_detail_obj.id,
                        'user_id': user_detail_obj.user_id.id,
                        'user_name': user_detail_obj.user_id.username,
                        'first_name': user_detail_obj.user_id.first_name,
                        'last_name': user_detail_obj.user_id.last_name,
                        'gender': user_detail_obj.gender,
                        'dob': user_detail_obj.dob,
                        'profile_pic': user_detail_obj.profile_pic.url if user_detail_obj.profile_pic else None
                    }
                    user_detail_list.append(user_detail_dict)
                else:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                user_details = UserDetail.objects.all().order_by('id')
                for user_detail in user_details:
                    user_detail_dict = {
                        'id' : user_detail.id,
                        'user_id': user_detail.user_id.id,
                        'user_name': user_detail.user_id.username,
                        'first_name': user_detail.user_id.first_name,
                        'last_name': user_detail.user_id.last_name,
                        'gender': user_detail.gender,
                        'dob': user_detail.dob,
                        'profile_pic': user_detail.profile_pic.url if user_detail.profile_pic else None
                    }
                    user_detail_list.append(user_detail_dict)

            return Response(user_detail_list, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            user_id = request.GET.get('user_id')
            print(user_id)
            data = request.data
            print(data)
            gender = data.get('gender')
            dob = data.get('dob')
            profile_pic = data.get('profile_pic')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')

            if user_id:
                user_detail_obj = UserDetail.objects.filter(user_id__id=user_id).first()
                user_obj = user_detail_obj.user_id
                print(user_detail_obj.user_id.first_name)
                if 'gender' in data:
                    user_detail_obj.gender = gender
                if 'dob' in data:
                    user_detail_obj.dob = dob
                if 'profile_pic' in data:
                    user_detail_obj.profile_pic = profile_pic
                if 'first_name' in data:
                    user_obj.first_name = first_name
                if 'last_name' in data:
                    user_obj.last_name = last_name
                if 'email' in data:
                    user_obj.email = email
                user_obj.save()
                user_detail_obj.save()
                return Response({"message":"user updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({'message':'user_id is not found'})
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetMessage(APIView):
    def get(self, request, *args, **kwargs):
        try:
            print(*args)
            print(*kwargs)
            message_list = list()
            sender_id = request.GET.get('sender_id')
            receiver_id = request.GET.get('receiver_id')

            message_objs = Message.objects.filter(
                (Q(sender=sender_id) & Q(receiver=receiver_id)) |
                (Q(sender=receiver_id) & Q(receiver=sender_id))
            ).order_by('timestamp')

            print(message_objs)

            for message_obj in message_objs:
                message_dict = dict()
                message_dict['sender'] = message_obj.sender.id
                message_dict['sender_name'] = message_obj.sender.first_name
                message_dict['receiver_id'] = message_obj.receiver.id
                message_dict['receiver_name'] = message_obj.receiver.first_name
                message_dict['message'] = message_obj.message
                message_dict['timestamp'] = message_obj.timestamp
                message_dict['is_read'] = message_obj.is_read
                message_dict['date'] = message_obj.timestamp.strftime('%Y-%m-%d')
                message_list.append(message_dict)

            grouped_messages = {}
            for date, group in groupby(message_list, key=lambda x: x['date']):
                grouped_messages[str(date)] = list(group)

            return JsonResponse({
                "message":'success',
                "result":True,
                "data":grouped_messages
            },status=status.HTTP_200_OK)
        
        except Exception  as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationApiView(APIView):
    def get(self, request):
        message = 'Success'
        result = False
        try:
            user_id = request.query_params.get('user_id')
            print(user_id)
            notification_objs = Notification.objects.filter(receiver__id=user_id).order_by('-id')
            serializer = NotificationSerializer(notification_objs, many=True)
            return JsonResponse({
                "message":message,
                "result":result,
                "data":serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({
                "message":"Failure",
                "result":False,
                "data":str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class NotificationReadApiView(APIView):
    def patch(self, request):
        try:
            user_id = request.query_params.get('user_id')
            if not user_id:
                return JsonResponse({
                    "message": "Failure",
                    "result": False,
                    "data": "user_id is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            data = request.data
            notification_ids = data.get('ids', [])
            print(notification_ids)

            # Fetch matching notifications
            notifications = Notification.objects.filter(receiver__id=user_id, id__in=notification_ids)
            if not notifications.exists():
                return JsonResponse({
                    "message": "Failure",
                    "result": False,
                    "data": "No matching notifications found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Bulk update
            notifications.update(read=True)

            return JsonResponse({
                "message": "Success",
                "result": True,
                "data": "Marked as read"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({
                "message": "Failure",
                "result": False,
                "data": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



class Sample(APIView):
    def get(self, request):
        try:
            return Response({'message':"sample"})
        except Exception as e:
            return Response({'message':'sampleee'})