from django.urls import include, path

from .views import classroom, students, teachers
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', classroom.home, name='home'),

    path('students/', include(([
        path('submit_details', students.StudentDetailsView.as_view(),
             name='submit_details'),
        path('profile/<str:name>', students.student_attendance_detail,
             name='student_details')
     ], 'classroom'), namespace='students')),

    path('teachers/', include(([
        path('',
             TemplateView.as_view(
              template_name='classroom/teachers/dashboard.html'),
             name='dashboard'),
        path('take_attendance', teachers.AttendanceView.as_view(),
             name='attendance'),
        path('taken_attendance_info/<int:pk>', teachers.taken_attendance_info,
             name='taken_attendance_info'),
        path('all_attendance_info', teachers.all_attendance_info,
             name='all_attendance_info'),
        path('download_attendance', teachers.download_attendance,
             name='download_csv'),
        path('students_list', teachers.students_list, name='students_list')
     ], 'classroom'), namespace='teachers')),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
