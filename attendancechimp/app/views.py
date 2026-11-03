"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io

from .models import Course, InstructorProfile, Lecture, QRCodeUpload, StudentProfile

# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)

CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

def index(request):
    """Render the home page (index.html)."""
    now = datetime.now(zoneinfo.ZoneInfo("America/Chicago"))
    context = {
        'current_time': now.strftime("%H:%M"),
        'user': request.user,
    }
    return render(request, 'app/index.html', context)

def time_view(request):
    now = datetime.now(zoneinfo.ZoneInfo("America/Chicago"))
    return HttpResponse(now.strftime("%H:%M"), content_type="text/plain")

def sum_view(request):
    try:
        int(request.GET["n1"])
        n1 = int(request.GET["n1"])
    except ValueError:
        n1 = float(request.GET["n1"])
    try:
        int(request.GET["n2"])
        n2 = int(request.GET["n2"])
    except ValueError:
        n2 = float(request.GET["n2"])
    return HttpResponse(f"<p>{json.dumps(n1 + n2)}</p>")

# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------

def new(request):
    if request.method == "GET":
        return render(request, 'app/new.html')
    else:
        return HttpResponse("Something went wrong", status=405)

@csrf_exempt
def createUser(request):
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_student = request.POST.get("is_student")

        if not user_name or not email or not password:
            return HttpResponse("Missing required fields", status=400)
        if User.objects.filter(email=email).exists():
            return HttpResponse("User with this email already exists", status=409)

        if User.objects.filter(username=user_name).exists():
            return HttpResponse("User with this username already exists", status=409)

        user = User.objects.create_user(
            username=user_name,
            email=email,
            password=password,
        )
        if is_student == "0":
            InstructorProfile.objects.create(user=user)
        else:
            StudentProfile.objects.create(user=user, student_id=user.id)

        user = authenticate(request, username=user_name, password=password)
        if user is not None:
            login(request, user)
        return HttpResponse(f"User {user_name} created and logged in successfully", status=200)
    else:
        return HttpResponse("Something went wrong", status=405)

# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------
def new_course(request):
    if request.method == "GET":
        return render(request, 'app/new_course.html')
    else:
        return HttpResponse("Something went wrong", status=405)
@csrf_exempt
def create_Course(request):
    if request.user.is_authenticated == False or InstructorProfile.objects.filter(user=request.user).exists() == False:
        return HttpResponse("You are not logged in as an Instructor.", status=401)
    if request.method == "POST":
        course_name = request.POST.get("course-name")
        start_time = request.POST.get("start-time")
        end_time = request.POST.get("end-time")
        day_mon = request.POST.get("day-mon")
        day_tue = request.POST.get("day-tue")
        day_wed = request.POST.get("day-wed")
        day_thu = request.POST.get("day-thu")
        day_fri = request.POST.get("day-fri")

        days = ""
        if day_mon:
            days += "M"
        if day_tue:
            days += "T"
        if day_wed:
            days += "W"
        if day_thu:
            days += "Th"
        if day_fri:
            days += "F"

        if days == "" or not start_time or not end_time or not course_name:
            return HttpResponse("No meeting days selected, missing course name or start/end time", status=400)
        if Course.objects.filter(name=course_name).exists():
            return HttpResponse(f"Course {course_name} already exists", status=400)
        course = Course.objects.create(
            name=course_name,
            start_time=start_time,
            end_time=end_time,
            meeting_days=days,
            instructor=InstructorProfile.objects.get(user=request.user)
        )
        return HttpResponse(f"Course {course_name} created successfully", status=200)
    else:
        return HttpResponse("Something went wrong", status=405)

def new_lecture(request):
    if request.user.is_authenticated == False or InstructorProfile.objects.filter(user=request.user).exists() == False:
        return HttpResponse("You are not logged in as an Instructor.", status=401)
    courses = Course.objects.filter(instructor=InstructorProfile.objects.get(user=request.user))
    return render(request, "app/new_lecture.html", {"courses": courses})

@csrf_exempt
def create_Lecture(request):
    if request.user.is_authenticated == False or InstructorProfile.objects.filter(user=request.user).exists() == False:
        return HttpResponse("You are not logged in as an Instructor.", status=401)
    if request.method == "POST":
        lecture_name = request.POST.get("choice")

        if Course.objects.filter(name=lecture_name).exists() == False:
            return HttpResponse(f"Course {lecture_name} does not exist", status=400)
        lecture = Lecture.objects.create(
            course=Course.objects.get(name=lecture_name),
            date= datetime.now(zoneinfo.ZoneInfo("America/Chicago"))
        )
        return HttpResponse(f"Lecture for course {lecture_name} created successfully", status=200)
    else:
        return HttpResponse("Something went wrong", status=405)

def new_QRCodeUpload(request):
    if request.method == "GET":
        return render(request, "app/new_qr_upload.html")
    else:
        return HttpResponse("Something went wrong", status=405)

@csrf_exempt
def create_QRCodeUpload(request):
    if request.user.is_authenticated == False or StudentProfile.objects.filter(user=request.user).exists() == False:
        return HttpResponse("You are not logged in as a Student.", status=401)
    if request.method == "POST":
        image_upload = request.FILES.get("imageUpload")
        if image_upload:
            qr_upload = QRCodeUpload.objects.create(
                student=StudentProfile.objects.get(user=request.user),
                image=image_upload
            )
            return HttpResponse("QR code uploaded successfully", status=200)
        else:
            return HttpResponse("No image uploaded", status=400)
    else:
        return HttpResponse("Something went wrong", status=405)

def dumpUploads(request):
    if request.user.is_authenticated == False or InstructorProfile.objects.filter(user=request.user).exists() == False:
        return HttpResponse("You are not logged in as an Instructor.", status=401)
    uploads = QRCodeUpload.objects.all()
    data = [{"username": upload.student.user.username, "upload_time": upload.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")} for upload in uploads]
    return JsonResponse(data, safe=False)
# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



