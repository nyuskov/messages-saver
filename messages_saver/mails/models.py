from django.db import models


class Profile(models.Model):
    email = models.CharField(max_length=254)
    login = models.CharField(max_length=120)
    password = models.CharField(max_length=50)


class Message(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=998)
    subject = models.CharField(max_length=50)
    text = models.TextField()
    sended_at = models.DateTimeField()
    received_at = models.DateTimeField()


class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    data = models.FileField()
