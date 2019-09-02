from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:dashboard')
        else:
            return redirect('students:student_details',
                            name=request.user.username)
    return render(request, 'classroom/home.html')
