from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView
from django.http import HttpResponse
from ..decorators import student_required
from ..forms import (StudentSignUpForm, StudentDetailsForm)
from ..models import User, StudentDetails,  AttendanceRecord, Attendance
from collections import Counter
from math import floor


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:submit_details')


@method_decorator([login_required, student_required], name='dispatch')
class StudentDetailsView(CreateView):
    model = StudentDetails
    form_class = StudentDetailsForm
    template_name = "classroom/students/student_details.html"

    def get_context_data(self, **kwargs):
        kwargs['success'] = "Congratulations ! You are now registered in the college."
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.user = self.request.user
        user.save()
        return redirect('students:student_details',
                        name=self.request.user.username)


def student_statistics(obj):
    obj_subject = []
    teacher_list = {}

    for i in obj:
        obj_subject.append(i.subject)
        teacher_list[i.subject] = i.teacher.username

    context = Counter(obj_subject)
    total_classes_context = {}
    print(teacher_list)

    for subject in context.keys():
        total = Attendance.objects.filter(subject=subject).count()
        attendance_percentage = floor((context[subject]/total)*100)
        total_classes_context[subject] = [context[subject], total,
                                          attendance_percentage,
                                          teacher_list[subject]]
    return total_classes_context


def student_attendance_detail(request, name):
    student = name
    print(name)
    obj = AttendanceRecord.objects.filter(
                    student__user__username=student)
    student_info = StudentDetails.objects.get(user__username=student)
    total_classes_context = student_statistics(obj)

    try:
        return render(request, 'classroom/students/student_info.html',
                      {'total_classes': total_classes_context,
                       'info': student_info})
    except:
        return render(request, 'classroom/students/student_info.html',
                      {'error': "No such student ID exists."})
