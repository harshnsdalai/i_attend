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
from ..forms import StudentSignUpForm, StudentDetailsForm
from ..models import User, StudentDetails


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

    def form_valid(self, form):

        user = form.save(commit=False)
        user.user = self.request.user
        user.save()
        return HttpResponse("Congratulations ! You are now registered in the college.")
