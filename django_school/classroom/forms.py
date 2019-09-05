from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from .models import User, Attendance, StudentDetails


class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user


class StudentSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        return user


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('branch', 'semester', 'image', 'subject')


class StudentDetailsForm(forms.ModelForm):
    class Meta:
        model = StudentDetails
        fields = ('branch', 'semester', 'image')


BRANCH_CHOICES = [('', '---------')] + [
        ('Information_Technology', 'Information_Technology'),
        ('CSE', 'CSE'),
        ('Electronics_and_Electrical_Engineering',
         'Electronics_and_Electrical_Engineering'),
        ('Mining', 'Mining'),
    ]


class DownloadCsv(forms.Form):
    year = forms.IntegerField(min_value=1950, max_value=2500)
    month = forms.IntegerField(min_value=1, max_value=12)
    date = forms.IntegerField(min_value=1, max_value=31)
    semester = forms.IntegerField(min_value=1, max_value=12)
    branch = forms.ChoiceField(choices=BRANCH_CHOICES)


class FilterForm(forms.Form):

    branch = forms.ChoiceField(choices=BRANCH_CHOICES, required=False)
    semester = forms.IntegerField(min_value=1, max_value=12, required=False)
