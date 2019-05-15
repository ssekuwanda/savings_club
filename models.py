from django.db import models
from django.urls import reverse
from django.conf import settings
from .utils import unique_slug_generator
from django.db.models.signals import pre_save, post_save

User = settings.AUTH_USER_MODEL

INTENTIONS = (
        ('Project','Project'),
        ('Tour','Tour'),
        ('Treatment','Treatment'),
        ('Leisure','Leisure'),
        ('Just','Just'),
        ('Others','Others'),
)

GENDER = (
        ('Male','Male'),
        ('Female','Female'),
)

class Club(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=122)
    saving_for = models.CharField(max_length=122, choices = INTENTIONS)
    slug = models.SlugField()
    timestamp = models.DateTimeField(auto_now_add=True) # This is to be called cake day

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("club_home", kwargs={"user":self.admin, "slug":self.slug})

def create_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(create_slug, sender=Club)

class ClubMember(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=122)
    last_name = models.CharField(max_length=122)
    phone_number = models.PositiveIntegerField()
    email_address = models.EmailField()
    gender = models.CharField(max_length=122, choices=GENDER, default='Male')
    snap = models.FileField(upload_to='boldclubs',null=True, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
            return str(self.first_name)+'-'+str(self.club)

class ClubSettings(models.Model):
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, related_name='clubsettings', null=True)
    deposit_date = models.PositiveIntegerField(null=True, blank=True) # like on every 30th of the month trigger a deposit initiation
    retry_deposit_date = models.PositiveIntegerField(null=True, blank=True) # If one wasnt able to deposit on the default date
    amount = models.PositiveIntegerField() # for graphing chart purposes only
    saving_till = models.DateField(null=True, blank=True) # Time expected to save for, Total time remaining
    cant_withdraw_before_above_date = models.BooleanField()
    total_amount = models.PositiveIntegerField(null=True, blank=True) # To be used for pie-chart (What is available Vs What is expected)

class MemberPw(models.Model): # with draws can be limited by password or saving_till
    member = models.ForeignKey(ClubMember, on_delete=models.CASCADE)
    password = models.CharField(max_length=220)
    password_confirmation = models.CharField(max_length=220)

    def __str__(self):
        return 'Member Passwords'

class MemberAmount(models.Model):
    club = models.ForeignKey(ClubMember, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)