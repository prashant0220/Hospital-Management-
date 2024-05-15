from django.db import models


# Create your models here.
class CustomUser(models.Model):
    # Add additional fields
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField('username', max_length=10, unique=True, db_index=True)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name


class Post(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blog_images/')
    summary = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'doctor'})
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    CATEGORY_CHOICES = (
        ('Mental Health', 'Mental Health'),
        ('Heart Disease', 'Heart Disease'),
        ('Covid19', 'Covid19'),
        ('Immunization', 'Immunization'),
        # Add more predefined categories as needed
    )
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General')

    def __str__(self):
        return self.title


class PatientAppointment(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointments')
    speciality = models.CharField(max_length=100)
    ap_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
