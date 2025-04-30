from django.db import models
from django.contrib.auth.models import User


class UserDetail(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    gender = models.CharField(max_length=200, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='user_profile/', blank=True, null=True)

    def __str__(self):
        return "{0}".format(self.id)



class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"
    
class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='message_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='message_receiver')
    read = models.BooleanField(default=False)
    content = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"

