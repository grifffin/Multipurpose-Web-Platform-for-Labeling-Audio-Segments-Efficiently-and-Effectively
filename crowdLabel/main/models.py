from django.contrib.auth.models import User
from django.db import models
from datetime import datetime


# Create your models here.


class UserType(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)


class File(models.Model):
    filename = models.CharField(max_length=100)
    file = models.FileField(upload_to='user_files')
    uploader = models.ForeignKey(User)
    upload_datetime = models.DateTimeField(default=datetime.now, blank=True)


class Study(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=200)
    segment_duration = models.DecimalField(max_digits=7, decimal_places=5)
    step_size = models.DecimalField(max_digits=7, decimal_places=5)
    max_total_responses = models.IntegerField()
    max_responses_per_worker = models.IntegerField(null=True, blank=True)
    min_responses_per_segment = models.IntegerField()
    max_responses_per_segment = models.IntegerField()
    threshold = models.IntegerField()
    code = models.CharField(max_length=100)
    creation_datetime = models.DateTimeField(default=datetime.now, blank=True)


class Label(models.Model):
    label_title = models.CharField(max_length=200)
    study = models.ForeignKey(Study)


class StudyFile(models.Model):
    study = models.ForeignKey(Study)
    file = models.ForeignKey(File)


class StudyWorker(models.Model):
    study = models.ForeignKey(Study)
    worker = models.ForeignKey(User)


class Segment(models.Model):
    start = models.DecimalField(max_digits=10, decimal_places=5)
    stop = models.DecimalField(max_digits=10, decimal_places=5)
    duration = models.DecimalField(max_digits=7, decimal_places=5)
    file = models.ForeignKey(File)
    study = models.ForeignKey(Study)
    status = models.CharField(max_length=13, default='low_priority')
    final_label = models.ForeignKey(Label, null=True, blank=True)


class Response(models.Model):
    label = models.ForeignKey(Label)
    user = models.ForeignKey(User, null=True)
    worker_id = models.CharField(max_length=100, null=True)
    label_datetime = models.DateTimeField(default=datetime.now, blank=True)
    segment = models.ForeignKey(Segment)
