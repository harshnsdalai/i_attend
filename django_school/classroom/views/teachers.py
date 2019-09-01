from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.http import HttpResponse
from ..decorators import teacher_required
from ..forms import TeacherSignUpForm, AttendanceForm, DownloadCsv, FilterForm
from ..models import User, Attendance, AttendanceRecord, StudentDetails
from django.utils.encoding import smart_str
import os
import csv


class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("teachers:dashboard")


@method_decorator([login_required, teacher_required], name='dispatch')
class AttendanceView(CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "classroom/teachers/attendance_details.html"

    def form_valid(self, form):

        user = form.save(commit=False)
        user.user = self.request.user
        user.save()
        return redirect("teachers:dashboard")


@login_required
@teacher_required
def download_attendance(request):
    form = DownloadCsv()
    if request.method == "POST":
        form = DownloadCsv(request.POST)
        if form.is_valid():
            user = request.user.username
            day = form.cleaned_data.get('date')
            year = form.cleaned_data.get('year')
            month = form.cleaned_data.get('month')
            date = str(year) + "-" + str(month) + "-" + str(day)
            semester = form.cleaned_data.get('semester')
            branch = form.cleaned_data.get('branch')
            obj = AttendanceRecord.objects.filter(
                teacher__username=user, date=date, branch=branch,
                semester=semester)

            path_to_file = str(day) + "/" + branch + "_" + str(semester) + ".csv"

            response = HttpResponse(content_type='text/csv')

            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(path_to_file)

            writer = csv.writer(response)
            writer.writerow(["List of Students present"])
            for i in obj:
                writer.writerow([i])
            return response
    return render(request, 'classroom/teachers/download_csv.html',
                  {'form': form})


def students_list(request):
    students = StudentDetails.objects.all()
    form = FilterForm()
    error = None
    if request.method == "GET":
        form = FilterForm(request.GET)
        if ('branch' and 'semester' in request.GET):
            students = StudentDetails.objects.filter(
                branch=request.GET['branch'], semester=request.GET['semester'])

        elif 'branch' in request.GET:
            students = StudentDetails.objects.filter(
                branch=request.GET['branch'])

        elif 'semester' in request.GET:
            students = StudentDetails.objects.filter(
                semester=request.GET['semester'])

        elif len(request.GET) != 0:
            return render(request, "404.html")

        if len(students) == 0:
            error = "Sorry no students in the respective Branch or Semester"
        else:
            error = None

    return render(request, 'classroom/teachers/students_list.html',
                  {'students': students, 'error': error, 'form': form})
