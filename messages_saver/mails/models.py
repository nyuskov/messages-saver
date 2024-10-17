from django.db import models


class MailUser(models.Model):
    email = models.CharField(max_length=254)
    login = models.CharField(max_length=120)
    password = models.CharField(max_length=50)


class Message(models.Model):
    user = models.ForeignKey(MailUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    description = models.TextField()
    sended_at = models.DateTimeField()
    received_at = models.DateTimeField()


class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    data = models.FileField()
