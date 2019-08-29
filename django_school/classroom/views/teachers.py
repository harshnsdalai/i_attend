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
from ..forms import TeacherSignUpForm, AttendanceForm, DownloadCsv
from ..models import User, Attendance
from django.utils.encoding import smart_str
import os



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
            date = form.cleaned_data.get('date')
            year = form.cleaned_data.get('year')
            month = form.cleaned_data.get('month')
            semester = form.cleaned_data.get('semester')
            branch = form.cleaned_data.get('branch')
            path_to_file = 'media/attendance/' + user + "/" + str(year) + "/" + str(month) + "/" + str(date) + "/" + branch + "_" + str(semester)+ ".csv"
            if os.path.exists(path_to_file):
                with open(path_to_file, 'rb') as fh:
                    
                    response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(path_to_file)
                    response['X-Sendfile'] = path_to_file
                    return response
    return render(request, 'classroom/teachers/download_csv.html', {'form': form})
