from django import forms
from django.utils import timezone

from redbusapp.models import *


class addBus(forms.ModelForm):
    class Meta:
        model = Bus
        exclude = ['total_seats']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter license number'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company'}),
            'rows': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter seat rows'}),
            'columns': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter seat columns'}),
        }


class addRoute(forms.ModelForm):
    class Meta:
        model = Route
        exclude = ['bus']
        widgets = {
            'time': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Enter time'}, format='%h:%m'),
            'City': forms.ModelChoiceField(to_field_name='location', queryset=City.objects.all()),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
        }


class JourneyForm(forms.Form):
    source = forms.ModelChoiceField(
        queryset=City.objects.all()
    )
    destination = forms.ModelChoiceField(
        queryset=City.objects.all()
    )
    journey_date = forms.DateField(
        widget=forms.SelectDateWidget(), label='Joining Date', initial=timezone.now()
    )


class BusForm(forms.Form):
    bus = forms.IntegerField(
        widget=forms.HiddenInput()
    )


class Preforget(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'})
    )


class PostForget(forms.Form):
    security_code = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter security code', 'class': 'form-control'})
    )


class resetpass(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-control form-change'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password again', 'class': 'form-control form-change'})
    )


class SeatsForm(forms.Form):
    seats = forms.CharField(
        widget=forms.HiddenInput(), max_length=100
    )


class SeatForm(forms.Form):
    seat = forms.CharField(
        max_length=2,
        widget=forms.HiddenInput()
    )
    row = forms.CharField(
        max_length=1, widget=forms.HiddenInput()
    )
    column = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    Name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter name'})
    )
    Age = forms.IntegerField(
        min_value=0,
        max_value=150,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter Age'})
    )
    gender = forms.ChoiceField(
        choices=((1, "Male"),
                 (2, "Female")),

    )


class ContactForm(forms.Form):
    Name = forms.CharField(
        max_length=100
    )
    Email = forms.EmailField()
    Mobile = forms.CharField(
        max_length=10
    )


class SignupForm(forms.Form):
    first_name = forms.CharField(
        max_length=75,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'})
    )
    last_name = forms.CharField(
        max_length=75,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'})
    )
    username = forms.CharField(
        max_length=75,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter User Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )
    password = forms.CharField(
        max_length=75,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )


class ProfileForm(forms.Form):
    phone = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone'})
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=75,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter User Name'})
    )
    password = forms.CharField(
        max_length=75,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )


class CancelForm(forms.Form):
    seats=forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )