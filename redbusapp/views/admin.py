from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView

from redbusapp.forms import addBus, addRoute
from redbusapp.models import Bus


class admin_add_bus(CreateView):
    template = 'add_bus.html'
    form_class = addBus

    def get(self, request, *args, **kwargs):
        form = addBus()
        return render(request, template_name='add_bus.html', context={'title': 'Add Bus', 'form': form})

    def post(self, request, *args, **kwargs):
        bus_form = addBus(request.POST)
        pk=0
        if bus_form.is_valid():
            bus = bus_form.save(commit=False)
            bus.total_seats = int(ord(request.POST['rows'].upper()) - 64) * int(request.POST['columns'])
            bus.save()
            pk=bus.id

        return redirect('redbus:add_route',pk=pk)


class admin_add_route(CreateView):
    template = 'add_route.html'
    form_class = addRoute

    def get(self, request, *args, **kwargs):
        form = addRoute()
        return render(request, template_name='add_route.html', context={'title': 'Add Route', 'form': form})

    def post(self, request, *args, **kwargs):
        route_form = addRoute(request.POST)
        if route_form.is_valid():
            bus = route_form.save(commit=False)
            bus.bus=Bus.objects.get(pk=kwargs.get('pk'))
            bus.save()

        return redirect('redbus:add_route',pk=kwargs.get('pk'))
