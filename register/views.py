import os
import string

from datetime import timedelta, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .models import CustomUser, Post, PatientAppointment


# Create your views here.

def Signup(request):
    if request.method == 'POST':
        # Extract form data
        user_type = request.POST.get('user_type')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        profile_picture = request.FILES.get('profile_picture')
        address = request.POST.get('address')

        user = CustomUser.objects.filter(username=username)
        if user:
            messages.warning(request, 'User already exist !')
            return redirect('signup')

        else:
            if password1 == password2:
                new_user = CustomUser.objects.create(user_type=user_type, first_name=first_name, last_name=last_name,
                                                     username=username, email=email, password=password1,
                                                     profile_picture=profile_picture,
                                                     address=address)
                request.session['registration_complete'] = True

                return redirect('register_success')

            else:
                messages.error(request, 'Password does not match with confirm password')
                return redirect('signup')

    return render(request, 'signup.html', )


def Login(request):
    if request.method == "POST":
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        try:
            user = CustomUser.objects.get(username=username)
            if user.password == password1:
                request.session['user_id'] = user.id
                request.session['registration_complete'] = True
                return redirect('dashboard')
            else:
                messages.error(request, 'Wrong password')
                return redirect('login')

        except:
            messages.warning(request, "No User exist Register first ")
            return redirect('login')
    return render(request, "login.html")


def success_register(request):
    if request.session.get('registration_complete', False):
        return render(request, 'registered.html')
    else:
        return redirect('signup')


def Dash(request):
    if request.session.get('registration_complete', False):
        user_id = request.session.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        img = user.profile_picture.url

        return render(request, "dash.html", {'author': user, 'img': img, })
    else:
        return redirect('signup')


def Logout(request):
    request.session['registration_complete'] = False
    return render(request, "logout.html")


def Posts(request):
    if request.session.get('registration_complete', False):
        categories = [choice[1] for choice in Post.CATEGORY_CHOICES]
        user_id = request.session.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        selected_category = request.GET.get('category')
        if user.user_type == 'doctor':
            if selected_category:
                posts = Post.objects.filter(author=user, category=selected_category).order_by('-id')
            else:
                posts = Post.objects.filter(author=user).order_by('-id')

            return render(request, "posts.html", {'author': user, 'posts': posts, 'categories': categories,
                                                  'selected_category': selected_category})
        else:
            # Filter posts based on the selected category
            if selected_category:
                posts = Post.objects.filter(category=selected_category).exclude(status='draft').order_by('-id')
            else:
                posts = Post.objects.exclude(status='draft').order_by('-id')

            return render(request, "posts.html", {'author': user, 'posts': posts, 'categories': categories,
                                                  'selected_category': selected_category})


def Create_Blog(request):
    if request.session.get('registration_complete', False):
        user_id = request.session.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        categories = [choice[1] for choice in Post.CATEGORY_CHOICES]
        if request.method == 'POST':
            author = user
            title = request.POST.get('title')
            summary = request.POST.get('summary')
            content = request.POST.get('content')
            category = request.POST.get('category')
            image = request.FILES.get('image')
            status = request.POST.get('status', 'published')

            post = Post(title=title, summary=summary, content=content,
                        category=category, image=image, status=status, author=author)
            post.save()
            return redirect(reverse('dashboard'))

        return render(request, "create_blog.html", {'author': user, 'categories': categories})


def Detail_Post(request, post_id):
    if request.session.get('registration_complete', False):
        user_id = request.session.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        post = get_object_or_404(Post, id=post_id)
        return render(request, "post_detail.html", {'post': post, 'author': user})


def publish_post(request, post_id):
    if request.session.get('registration_complete', False):
        post = get_object_or_404(Post, id=post_id)
        post.status = 'published'
        post.save()
        return redirect('posts')


def doctors(request):
    if request.session.get('registration_complete', False):
        user_id = request.session.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        doctors = CustomUser.objects.filter(user_type='doctor')
        return render(request, "doctors.html", {'author': user, 'doctors': doctors})


def Appointment_book(request, doctor_id):
    if request.session.get('registration_complete', False):
        user_id = request.session.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        doctor = CustomUser.objects.get(id=doctor_id)
        if request.method == 'POST':
            speciality = request.POST.get('speciality')
            date_str = request.POST.get('datee')
            time_str = request.POST.get('start time')

            date = datetime.strptime(date_str, '%Y-%m-%d')
            start_time = datetime.strptime(time_str, '%H:%M')
            end_time = start_time + timedelta(minutes=45)

            appointment = PatientAppointment.objects.create(patient=user, doctor=doctor, speciality=speciality,
                                                            ap_date=date,
                                                            start_time=start_time, end_time=end_time)
            appointment.save()
            create_google_calender_event(appointment)
            return redirect('booked')
    return render(request, "book_appointment.html", {'doctor': doctor, })


def booked(request):
    if request.session.get('registration_complete', False):
        return render(request, 'booked.html')
    else:
        return redirect('signup')


def myappointment(request):
    if request.session.get('registration_complete', False):
        user_id = request.session.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        appointments = PatientAppointment.objects.filter(doctor=user)
        return render(request, "my_appointment.html", {'appointments': appointments})


def create_google_calender_event(appointment):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        # flow.server.shutdown()

    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': 'Appointment with ' + appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        'Location': "800 Howard St., San Francisco, CA 94103",
        'description': 'Appointment with ' + appointment.doctor.first_name + ' ' + appointment.doctor.last_name,
        'start': {
            'dateTime': appointment.ap_date.isoformat() + 'T' + appointment.start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': appointment.ap_date.isoformat() + 'T' + appointment.end_time.isoformat(),
            'timeZone': 'UTC',
        },

    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get('id')


