import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Notification
from urllib.parse import parse_qs

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Attempting WebSocket connection...")

        query_params = parse_qs(self.scope['query_string'].decode())
        sender_id = query_params.get('sender_id', [None])[0]
        receiver_id = query_params.get('receiver_id', [None])[0]

        if sender_id and receiver_id:
            self.sender_id = int(sender_id)
            self.receiver_id = int(receiver_id)
            sender = await self.get_user(self.sender_id)
            receiver = await self.get_user(self.receiver_id)

            if sender and receiver:
                self.sender_group_name = f"user_{self.sender_id}"
                self.receiver_group_name = f"user_{self.receiver_id}"

                await self.channel_layer.group_add(self.sender_group_name, self.channel_name)
                await self.channel_layer.group_add(self.receiver_group_name, self.channel_name)

                await self.accept()
                print(f"WebSocket connected: Sender={sender.username}, Receiver={receiver.username}")
            else:
                print("Connection failed: Invalid sender or receiver.")
                await self.close()
        else:
            print("Connection failed: Missing sender_id or receiver_id.")
            await self.close()

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: Sender={getattr(self, 'sender_id', None)}, Receiver={getattr(self, 'receiver_id', None)}")

        if hasattr(self, 'sender_group_name'):
            await self.channel_layer.group_discard(self.sender_group_name, self.channel_name)

        if hasattr(self, 'receiver_group_name'):
            await self.channel_layer.group_discard(self.receiver_group_name, self.channel_name)

    async def receive(self, text_data):
        print("Message received...")
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message')

        saved_message = await self.save_message(self.sender_id, self.receiver_id, message_content)
        saved_notification = await self.save_notification(self.sender_id, self.receiver_id, message_content)
        print("Debug - Saved message:", saved_message.message, saved_message.timestamp)

        message_data = {
            'type': 'chat_message',
            'sender': self.sender_id,
            'receiver': self.receiver_id,
            'message': saved_message.message,
            'timestamp': saved_message.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }

        notification_data = {
            'type': 'send_notification',
            'sender': self.sender_id,
            'receiver': self.receiver_id,
            'message': saved_notification.content,
        }

        # Send messages to both sender and receiver
        await self.channel_layer.group_send(self.sender_group_name, message_data)
        await self.channel_layer.group_send(self.receiver_group_name, message_data)

        # Send notification to the receiver
        await self.channel_layer.group_send(f"user_notifications_{self.receiver_id}", notification_data)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'receiver': event['receiver'],
            'message': event['message'],
            'timestamp': event.get('timestamp') 
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        return Message.objects.create(sender_id=sender_id, receiver_id=receiver_id, message=content)

    @database_sync_to_async
    def save_notification(self, sender_id, receiver_id, content):
        """Save a notification for the receiver."""
        return Notification.objects.create(sender_id=sender_id, receiver_id=receiver_id, content=content)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope['query_string'].decode())
        self.user_id = query_params.get('user_id', [None])[0]

        if self.user_id:
            self.user_id = int(self.user_id)
            self.group_name = f"user_notifications_{self.user_id}"

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            print(f"WebSocket connected for notifications: User={self.user_id}")

        else:
            print("WebSocket connection failed: No user_id provided.")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        """Send notification data to the frontend."""
        await self.send(text_data=json.dumps({
            'notification': event['message']
        }))
