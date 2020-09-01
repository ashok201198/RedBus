import random

from django.core.mail import send_mail
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.views.generic import CreateView

from redbusapp.models import User, Profile, PasswordReset
from django.shortcuts import render, redirect

from redbusapp.forms import SignupForm, LoginForm, ContactForm, ProfileForm, Preforget, PostForget, resetpass


class SignupUser(CreateView):
    template_name = 'registration.html'
    model = User
    form_class = SignupForm

    def get(self, request, *args, **kwargs):
        form = SignupForm()
        contact = ProfileForm()
        return render(request, template_name='registration.html',
                      context={'title': 'Add User', 'form': form, 'contact': contact})

    def post(self, request, *args, **kwargs):
        user_form = SignupForm(request.POST)
        # import ipdb
        # ipdb.set_trace()
        if user_form.is_valid():
            check = User.objects.filter(username=request.POST['username'])
            if check:
                form = SignupForm()
                contact = ProfileForm()
                return render(request, template_name='registration.html',
                              context={'title': 'Add User', 'form': form, 'contact': contact,
                                       'error': 'username already taken'})
            check = User.objects.filter(email=request.POST['email'])
            if check:
                form = SignupForm()
                contact = ProfileForm()
                return render(request, template_name='registration.html',
                              context={'title': 'Add User', 'form': form, 'contact': contact,
                                       'error': 'email\'s already taken'})
            user = User.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'],
                                       username=request.POST['username'], email=request.POST['email'])
            user.set_password(request.POST['password'])
            user.save()
            user1 = User.objects.get(username=request.POST['username'])
            profile = Profile.objects.create(user_id=user1.pk, phone=request.POST['phone'])
            profile.save()
            user = authenticate(
                request,
                username=user_form.cleaned_data['username'],
                password=user_form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('redbus:journey')
            else:
                return redirect('redbus:register')


class LoginUser(View):
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, template_name='login.html', context={'title': 'Validate User', 'form': form})

    def post(self, request, *args, **kwargs):
        user_form = LoginForm(request.POST)
        if user_form.is_valid():
            user = authenticate(
                request,
                username=user_form.cleaned_data['username'],
                password=user_form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('redbus:journey')
            else:
                form = LoginForm()
                return render(request, template_name='login.html', context={'title': 'Validate User', 'form': form,
                                                                            'error': 'Either user name or password is incorrect'})


def LogoutUser(request):
    logout(request)
    return redirect('redbus:login')


class Prereset(View):

    def get(self, request, *args, **kwargs):
        form = Preforget()
        return render(request, template_name='preforget.html', context={'title': 'Reset Stage-1', 'form': form})

    def post(self, request, *args, **kwargs):
        form = Preforget(request.POST)
        user = User.objects.get(email=request.POST['email'])
        code = random.randint(100000, 999999)
        if user:
            request.session['forgot_email'] = request.POST['email']
            PasswordReset.objects.filter(user=user).delete()
            PasswordReset.objects.create(user=user, security_code=str(code))
            message = f"Your security code is " + (str(code))
            send_mail(subject="Password Reset", message=message, from_email="yourbusdjango@gmail.com",
                      recipient_list=[request.POST['email']], fail_silently=False)
        else:
            return render(request, template_name='preforget.html', context={'title': 'Reset Stage-1', 'form': form,
                                                                            'error': "Enter valid email(i.e., already registered)"})
        return redirect('redbus:stage2')


class reset(View):

    def get(self, request, *args, **kwargs):
        form = PostForget()
        return render(request, template_name='postforget.html', context={'title': 'Reset Stage-2', 'form': form})

    def post(self, request, *args, **kwargs):
        form = PostForget(request.POST)
        email = request.session.get('forgot_email')
        user = User.objects.get(email=email)
        code = PasswordReset.objects.filter(user=user).values_list('security_code')
        if str(code[0][0]) == str(request.POST['security_code']):
            return redirect('redbus:reset')
        else:
            form = PostForget()
            return render(request, template_name='postforget.html',
                          context={'title': 'Reset Stage-2', 'form': form, 'error': "Incorrect security code"})


class changepass(View):

    def get(self, request):
        form = resetpass()
        return render(request, template_name='reset.html',
                      context={'title': 'Change Password', 'form': form, 'proceed': True})

    def post(self, request):
        form = resetpass(request.POST)
        if not form['password'].data == form['confirm_password'].data:
            form = resetpass()
            return render(request, template_name='reset.html',
                          context={'title': 'Change Password', 'form': form, 'proceed': True,
                                   'error': 'Passwords dosent match'})
        email = request.session.get('forgot_email')
        user = User.objects.get(email=email)
        user.set_password(request.POST['password'])
        user = authenticate(request, username=user.username, password=request.POST['password'])
        login(request, user)
        return redirect('redbus:journey')
