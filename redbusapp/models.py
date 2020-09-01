from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

class City(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class PasswordReset(models.Model):
    user=models.ForeignKey(User,on_delete=models.DO_NOTHING)
    security_code=models.CharField(max_length=6)

    def __str__(self):
        return self.user.username

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)

    def __str__(self):
        return self.user.first_name


class Bus(models.Model):
    number = models.CharField(max_length=10)
    company = models.CharField(max_length=15)
    rows = models.CharField(max_length=1, validators=[MaxValueValidator('h')])
    columns = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    total_seats = models.IntegerField()

    def __str__(self):
        return self.number


class Route(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    time = models.TimeField(blank=False)
    location = models.ForeignKey(City, on_delete=models.CASCADE)
    price = models.IntegerField(blank=False)

    def __str__(self):
        return self.bus.number


class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Seats(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    row = models.CharField(max_length=1, validators=[MaxValueValidator('h')])
    column = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    vacant = models.BooleanField(default=False)
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=6)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    user=models.ForeignKey(User,on_delete=models.DO_NOTHING)
    contact=models.ForeignKey(Contact,on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class source(models.Model):
    name = models.ForeignKey(City, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    bus = models.ForeignKey(Bus, on_delete=models.DO_NOTHING)
    seat = models.ForeignKey(Seats, on_delete=models.DO_NOTHING)
    date = models.DateField()
    source = models.ForeignKey(source, on_delete=models.DO_NOTHING)
    destination = models.ForeignKey(City, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.user.first_name
