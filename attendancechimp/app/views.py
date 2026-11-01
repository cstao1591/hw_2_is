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

from .models import InstructorProfile, StudentProfile

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

        if User.objects.filter(email=email).exists():
            return HttpResponse("User with this email already exists", status=409)

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



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



