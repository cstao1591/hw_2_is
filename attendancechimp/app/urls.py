from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('time', views.time_view, name='time'),
    path('sum', views.sum_view, name='sum'),
    path('', views.index, name='home'),
    path('index.html', views.index, name='index_html'),
    path('new', views.new, name='new'),
    path('createUser', views.createUser, name='createUser'),
    path('createLecture', views.create_Lecture, name='createLecture'),
    path('newLecture', views.new_lecture, name='newLecture'),
    path('newCourse', views.new_course, name='newCourse'),
    path('createCourse', views.create_Course, name='createCourse'),
    path('newQRCodeUpload', views.new_qr_upload, name='new_qr_upload'),
    path('createQRCodeUpload', views.create_QRCodeUpload, name='createQRCodeUpload'),
    path('dumpUploads', views.dumpUploads, name='dumpUploads'),
]
