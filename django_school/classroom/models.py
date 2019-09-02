import os
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from facenet.algo import input_embeddings, recognize_faces_in_cam, TrainImage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
today = datetime.datetime.today()


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


def teacher_directory_path(instance, filename):
    file_type = "." + filename.split('.')[-1]
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'attendance_images/{0}/{1}/{2}/{3}/{4}'.format(
        instance.user.username, today.year, today.month, today.day,
        instance.branch + "_" + str(instance.semester) + file_type)


def student_directory_path(instance, filename):
    file_type = "." + filename.split('.')[-1]
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'embeddings/{0}'.format(
        instance.user.username + file_type)


BRANCH_CHOICES = [
        ('Information_Technology', 'Information_Technology'),
        ('CSE', 'CSE'),
        ('Electronics_and_Electrical_Engineering',
         'Electronics_and_Electrical_Engineering'),
        ('Mining', 'Mining'),
    ]


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    semester = models.IntegerField()
    image = models.ImageField(upload_to=teacher_directory_path)
    count = models.IntegerField(default=0)
    date = models.DateField(default=today)
    count_added = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + self.branch


class StudentDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    semester = models.IntegerField()
    image = models.ImageField(upload_to=student_directory_path)

    def __str__(self):
        return self.user.username


class AttendanceRecord(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentDetails, on_delete=models.CASCADE)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    semester = models.IntegerField()
    date = models.DateField()
    subject = models.CharField(max_length=50)

    def __str__(self):
        return self.student.user.username


@receiver(post_save, sender=Attendance, dispatch_uid="pass_image")
def pass_image_to_neural_net(sender, instance, **kwargs):
    image_url = instance.image.url[1::]
    #attendance_data = {'record': ['harsh', 'manav', 'tandon'], 'count': 50 }
    attendance_data = recognize_faces_in_cam(input_embeddings, image_url)
    record = attendance_data['record']
    teacher = instance.user
    branch = instance.branch
    semester = instance.semester
    subject = instance.subject

    if not instance.count_added:

        q = Attendance.objects.get(id=instance.id)
        q.count = attendance_data['count']
        q.count_added = True
        q.save()
        return
    print("Pass image to neural net:The detected identity in pic uploaded by teacher are = ", record)
    for i in record:
        id = i.split('_')[-1]
        print(i)
        student = get_object_or_404(StudentDetails, pk=int(id))# StudentDetails.objects.get(user__username=i)
        r = AttendanceRecord(teacher=teacher, subject=subject, student=student, semester=semester, branch=branch, date=today)
        r.save()


@receiver(post_save, sender=StudentDetails, dispatch_uid="train_image")
def train_image(sender, instance, **kwargs):
    url = instance.image.url[1::]
    print('url=', url)
    TrainImage(url, instance.user.username + "_" + str(instance.id))
