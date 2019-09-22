from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
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
from classroom.views.students import student_statistics


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
        return redirect("teachers:taken_attendance_info", pk=user.id)


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

            path_to_file = str(date) + "/" + branch + "_" + str(semester) + ".csv"

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

    form = FilterForm(request.GET)

    if 'branch' and 'semester' in request.GET:
        if request.GET['branch'] != '' and request.GET['semester'] != '':
            students = StudentDetails.objects.filter(
                branch=request.GET['branch'], semester=request.GET['semester'])
        elif request.GET['branch'] != '':
            students = StudentDetails.objects.filter(
                branch=request.GET['branch'])
        elif request.GET['semester']:
            students = StudentDetails.objects.filter(
                        semester=request.GET['semester'])
        else:
            students = StudentDetails.objects.all()

    elif len(request.GET) != 0:
        return render(request, "404.html")

    else:
        students = StudentDetails.objects.all()
    status_dict = {}
    for student in students:
        status_dict[student.user.username] = is_regular(student.user.username)
    print(status_dict)

    return render(request, 'classroom/teachers/students_list.html',
                  {'students': students, 'form': form,
                   'status': status_dict})


def is_regular(student):
    obj = AttendanceRecord.objects.filter(
                    student__user__username=student)
    total_classes = student_statistics(obj)
    min = 50
    status = 'Regular'
    for values in total_classes.values():
        if values[2] < min:
            status = 'Not Regular'
            break
    return status


def taken_attendance_info(request, pk):
    attendance_obj = get_object_or_404(Attendance, pk=pk)
    return render(request, 'classroom/teachers/taken_attendance_info.html',
                  {'attendance_info': attendance_obj})


def all_attendance_info(request):
    attendance_obj = Attendance.objects.filter(user=request.user).order_by('-date')
    return render(request, 'classroom/teachers/all_attendance_info.html',
                  {'attendance_info': attendance_obj})
