import datetime

from django.core.mail import send_mail
from django.utils import timezone

from django.shortcuts import render, redirect
from django.views.generic import ListView

from redbusapp.forms import JourneyForm, BusForm, SeatsForm, SeatForm, ContactForm
from redbusapp.models import Bus, Route, Ticket, Contact, Seats, source, City


class Get_Journey(ListView):
    template_name = 'journey.html'
    form_class = JourneyForm

    def get(self, request, *args, **kwargs):
        form = JourneyForm()
        return render(request, template_name='journey.html', context={'title': 'Select Journey', 'form': form})

    def post(self, request, *args, **kwargs):
        user_form = JourneyForm(request.POST)

        date, month, year = timezone.now().day, timezone.now().month, timezone.now().year
        hsh = date + month * 13 + year * 365
        cmp = int(request.POST['journey_date_day']) + (int(request.POST['journey_date_month']) * 13) + (
                int(request.POST['journey_date_year']) * 365)
        hsh2 = date + (month + 1) * 13 + year * 365
        if hsh <= cmp:
            if request.POST['source'] == request.POST['destination']:
                return render(request, 'journey.html',
                              {'form': user_form, 'error_message': 'Source and destination can\'t be the same'})
            elif cmp > hsh2:
                return render(request, 'journey.html',
                              {'form': user_form,
                               'error_message': 'Advance booking can be done only for a month duration'})
            else:
                request.session['source'] = request.POST['source']
                request.session['destination'] = request.POST['destination']
                request.session['journey_date_day'] = request.POST['journey_date_day']
                request.session['journey_date_month'] = request.POST['journey_date_month']
                request.session['journey_date_year'] = request.POST['journey_date_year']
                return redirect('redbus:buses')
        else:
            return render(request, 'journey.html', {'form': user_form, 'error_message': 'Not a Valid Date'})


class Get_buses(ListView):
    template_name = 'view_bus.html'

    def get_queryset(self):
        source = self.request.session.get('source')
        destination = self.request.session.get('destination')
        sday = self.request.session.get('journey_date_day')
        smonth = self.request.session.get('journey_date_month')
        syear = self.request.session.get('journey_date_year')
        date, month, year = timezone.now().day, timezone.now().month, timezone.now().year
        hsh = date + month * 13 + year * 365
        error = ""
        self.request.session['error'] = error
        cmp = int(sday) + int(smonth) * 13 + int(syear) * 365
        if hsh == cmp:
            flag = 1
            z = datetime.datetime.now() + datetime.timedelta(minutes=30)
            hsh = int(z.day) + (int(z.month) * 13) + (int(z.year) * 365)
            if hsh == cmp:
                routes_s = Route.objects.filter(location_id=source).filter(
                    time__gte=(z))
                routes_d = Route.objects.filter(location_id=destination).filter(
                    time__gte=z)
            else:
                error = "Showing Buses for tomorrow"
                self.request.session['error'] = error
                self.request.session['journey_date_day'] = z.day
                self.request.session['journey_date_month'] = z.month
                self.request.session['journey_date_year'] = z.year
                routes_s = Route.objects.filter(location_id=source)
                routes_d = Route.objects.filter(location_id=destination)
        else:
            routes_s = Route.objects.filter(location_id=source)
            routes_d = Route.objects.filter(location_id=destination)

        x = list(routes_s)
        y = list(routes_d)
        a = []
        for i in x:
            if {'bus_id': i.bus_id} in list(routes_d.values('bus_id')):
                m = Route.objects.filter(bus_id=i.bus_id).get(location_id=destination)
                if m.price - i.price > 0:
                    a.append(
                        {'bus_id': i.bus_id, 'bus_price': m.price - i.price, 'arrival': i.time, 'departure': m.time})
        return a

    def get(self, request, *args, **kwargs):
        a = self.get_queryset()
        user_form = JourneyForm()
        error = request.session['error']
        if a == []:
            error = "No buses Found"
            return redirect('redbus:journey')
        form = BusForm()
        return render(request, template_name='bus.html',
                      context={'title': 'Select Journey', 'form': form, 'buses': a, 'error': error})

    def post(self, request, *args, **kwargs):
        form = BusForm(request.POST)
        if form.is_valid():
            x = int(form['bus'].value())
            request.session['bus'] = x
            buses = self.get_queryset()
            for i in buses:
                if i['bus_id'] == int(x):
                    request.session['arrival'] = i['arrival'].strftime('%X')
                    request.session['depart'] = i['departure'].strftime('%X')
                    break
            return redirect('redbus:seats')
        else:
            return render(request, template_name='bus.html',
                          context={'title': 'Select Journey', 'error': 'Bus_form not valid'})


class Get_seats(ListView):
    template = 'view_bus.html'

    def get_queryset(self):
        bus_id = self.request.session.get('bus')
        source = self.request.session.get('source')
        destination = self.request.session.get('destination')
        sday = self.request.session.get('journey_date_day')
        smonth = self.request.session.get('journey_date_month')
        syear = self.request.session.get('journey_date_year')
        price = Route.objects.filter(bus_id=bus_id).get(location=destination).price - Route.objects.filter(
            bus_id=bus_id).get(location=source).price
        self.request.session['price'] = price
        cities = list(Route.objects.filter(bus_id=bus_id).values_list('location'))
        times = list(Route.objects.filter(bus_id=bus_id).values_list('time'))
        z = [x for _, x in sorted(zip(times, cities), key=lambda pair: pair[0])]
        bus1 = Bus.objects.get(pk=bus_id)
        seat = [0] * (ord(bus1.rows) - 64) * (bus1.columns)
        dest = 0
        src = 0
        for i in range(len(z)):
            if z[i][0] == int(source):
                src = i
            if z[i][0] == int(destination):
                dest = i
        i = 0
        seats = []
        while i != dest:
            for j in range(i + 1, len(z)):
                if j != src:
                    seats += Ticket.objects.filter(date__year=int(syear)).filter(date__month=int(smonth)).filter(
                        date__day=int(sday)).filter(
                        bus_id=int(bus_id)).filter(source__name_id=int(z[i][0])).filter(
                        destination_id=int(z[j][0])).values_list(
                        'seat__row', 'seat__column')
            i += 1
        # seats = Ticket.objects.filter(date__year=int(syear)).filter(date__month=int(smonth)).filter(
        #     date__day=int(sday)).filter(
        #     bus_id=int(bus_id)).filter(source__name_id=int(source)).filter(destination_id=int(destination)).values_list(
        #     'seat__row', 'seat__column')
        return seats, seat

    def get(self, request, *args, **kwargs):
        seats, seat = self.get_queryset()
        bus_id = self.request.session.get('bus')
        price = request.session.get('price')
        rows = Bus.objects.get(pk=bus_id).rows
        columns = Bus.objects.get(pk=bus_id).columns
        form = SeatsForm()
        x = [str(i[0]) + str(i[1]) for i in seats]
        request.session['seats'] = x
        return render(request, template_name='view_bus.html', context={
            'title': 'Select Seats',
            'seats': [str(i[0]) + str(i[1]) for i in seats],
            'rows': [chr(i) for i in range(ord('A'), ord(rows) + 1)],
            'columns': [i for i in range(1, columns + 1)],
            'form': form,
            'price': price
        })

    def post(self, request, *args, **kwargs):
        seats = SeatsForm(request.POST)
        if seats.is_valid():
            seat = seats['seats'].value().split(',')
            seat = seat[:-1]
            booked = request.session.get('seats')
            error = None
            bus_id = self.request.session.get('bus')
            price = request.session.get('price')
            rows = Bus.objects.get(pk=bus_id).rows
            columns = Bus.objects.get(pk=bus_id).columns
            form = SeatsForm()
            x = [str(i[0]) + str(i[1]) for i in seat]
            request.session['seats'] = x
            for i in seat:
                if i.casefold() in booked:
                    return render(request, template_name='view_bus.html', context={
                        'title': 'Select Seats',
                        'seats': x,
                        'rows': [chr(i) for i in range(ord('A'), ord(rows) + 1)],
                        'columns': [i for i in range(1, columns + 1)],
                        'form': form,
                        'price': price,
                        'error': "Can manually update the booked seats",
                    })
            else:
                request.session['book'] = seat
                return redirect('redbus:details')


class get_details(ListView):
    template_name = 'details.html'

    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        seats_to_book = request.session.get('book')
        forms = []
        for i in seats_to_book:
            form = SeatForm()
            forms.append(form)
        contact = ContactForm()
        return render(request, template_name='details.html',
                      context={'title': 'Enter Passenger Details', 'forms': forms, 'contact': contact,
                               'seats': seats_to_book})

    def post(self, request, *args, **kwargs):
        pass
        form = ContactForm(request.POST)
        seats = request.session.get('book')
        bus = request.session.get('bus')
        if form.is_valid():
            request.POST = dict(request.POST)
            request.session['Names'] = request.POST['Name']
            request.session['genders'] = request.POST['gender']
            request.session['Age'] = request.POST['Age']
            contact = Contact.objects.create(name=request.POST['Name'][0], email=request.POST['Email'][0],
                                             phone=request.POST['Mobile'][0])
            contact.save()
            request.session['Email'] = request.POST['Email'][0]
            j = 1
            bus1 = Bus.objects.get(pk=bus)
            sday = self.request.session.get('journey_date_day')
            smonth = self.request.session.get('journey_date_month')
            syear = self.request.session.get('journey_date_year')
            sourcer = self.request.session.get('source')
            destination = self.request.session.get('destination')
            for i in seats:
                gender = ''
                if request.POST['gender'][j - 1] == '1':
                    gender = 'Male'
                else:
                    gender = 'Female'
                seat = Seats.objects.create(bus_id=bus, row=i[0], column=i[1],
                                            name=request.POST['Name'][j], vacant=False, gender=gender,
                                            age=request.POST['Age'][j - 1], user_id=request.user.id,
                                            contact_id=contact.pk)
                seat.save()
                source1 = source.objects.create(name_id=sourcer)
                ticket = Ticket.objects.create(seat_id=seat.id,
                                               date=str(str(syear) + '-' + str(smonth) + '-' + str(sday)),
                                               bus_id=bus1.pk, destination_id=int(destination),
                                               source_id=int(source1.pk), user_id=request.user.id)
                ticket.save()
                j += 1

            return redirect('redbus:confirmation')
        else:
            seats_to_book = request.session.get('book')
            forms = []
            for i in seats_to_book:
                form = SeatForm()
                forms.append(form)
            contact = ContactForm()
            return render(request, template_name='details.html',
                          context={'title': 'Enter Passenger Details', 'forms': forms, 'contact': contact,
                                   'seats': seats_to_book, 'error': "Enter details correctly"})

def get_string1(bus, sday, smonth, syear, src, dest, arv, dept):
    return '''<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Your Site</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="">
        <meta name="author" content="">

        <link rel="stylesheet" href="https://bootswatch.com/4/lux/bootstrap.min.css">
        <link href="http://getbootstrap.com/2.3.2/assets/css/bootstrap-responsive.css" rel="stylesheet">
    </head>

    <body>
<div class="container-fluid">
        <h2 align="center">Happy Journey</h2>
        <h4 align="center">
            Bus Number:''' + bus.number + '''
            &nbsp;&nbsp;
            Journey Date: ''' + str(str(sday) + '-' + str(smonth) + '-' + str(syear)) + '''
            &nbsp;&nbsp;
            <br>
            Source: ''' + str(src) + '''
            &nbsp;&nbsp;
            Arrival Time: ''' + str(arv) + '''
            &nbsp;&nbsp;
            <br>
            Destination: ''' + str(dest) + '''
            &nbsp;&nbsp;
            Departure Time: ''' + str(dept) + '''
        </h4>
        <br>
        <h4><table align ="center" class="table-bordered tab-content">
            <th>Name</th>
            <th>Age</th>
            <th>Sex</th>
            <th>Seat</th>
    '''


def get_string(bus, sday, smonth, syear, src, dest, arv, dept):
    return """<html><body style="background: url(https://subtlepatterns.com/patterns/broken_noise.png);">
    <div style=
        "margin: 0px auto;
        margin-top: 80px;
        background: #FFF9EE url(https://subtlepatterns.com/patterns/lightpaperfibers.png);
        color: #333;
        text-transform: uppercase;
        padding: 8px;
        min-width: 600px;
        font-weight: bold;
        text-shadow: 0px 1px 0px #fff;
        font-size: 11px;
        border-left: 1px dashed rgba(51, 51, 51, 0.5);
        -webkit-filter: drop-shadow(0 5px 18px #000);">
        <div style=
            "border: 2px dashed rgba(51, 51, 51, 0.5);
            min-height: 100px;
            padding: 8px;
            min-width: 600px;
            padding: 5px 0px;
            margin: 0px;
            font-size: 18px;
            border-bottom: 1px solid rgba(51, 51, 51, 0.3);
            text-align: center;">
            <h1 style=
                "padding: 5px 0px;
                margin: 0px;
                font-size: 18px;
                border-bottom: 1px solid rgba(51, 51, 51, 0.3);
                text-align: center;">
                Happy Journey</h1>
            <div style=
                "width: 100%;
                margin: 8px;
                margin-top: 5px;
                 float: left;
                padding: 5px;
                min-width: 83px;
                text-align: center;">
                <div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Bus<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(bus) + """</h6></div>
                <div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Date<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(sday) + '-' + str(smonth) + '-' + str(syear) + """</h6></div>
                <div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Source<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(source) + """</h6></div>
                <div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Destination<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(dest) + """</h6></div>
            </div>
            <div style=
                "width: 100%;
                margin-top: 5px;
                 float: left;
                 margin: 8px;
                padding: 5px;
                min-width: 83px;
                text-align: center;">
                <div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Arrival<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(arv) + """</h6></div>
                <div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">ET Reach<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(dept) + """</h6></div>
            </div>
            <div style=
                "width: 100%;
                margin-top: 5px;
                 float: left;
                 margin: 8px;
                padding: 5px;
                min-width: 83px;
                text-align: center;">
    """

class get_ticket(ListView):
    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        seats = request.session.get('tickets')
        seat = request.session.get('book')
        bus = request.session.get('bus')
        posters = []
        j = 0
        names = request.session.get('Names')[1:]
        genders = request.session.get('genders')
        ages = request.session.get('Age')
        bus = Bus.objects.get(pk=bus)
        sday = self.request.session.get('journey_date_day')
        smonth = self.request.session.get('journey_date_month')
        syear = self.request.session.get('journey_date_year')
        source = self.request.session.get('source')
        destination = self.request.session.get('destination')
        price = int(self.request.session.get('price')) * (len(names))
        src = City.objects.get(pk=int(source))
        dest = City.objects.get(pk=int(destination))
        depart = request.session.get('depart')
        arrival = request.session.get('arrival')
        string = get_string(bus, sday, smonth, syear, src, dest, arrival, depart)
        for i in seat:
            gender = ''
            if genders[j] == '1':
                gender = 'Male'
            else:
                gender = 'Female'
            genders[j] = gender
            name = names[j]
            gender = gender
            age = ages[j]
            user_id = request.user.id
            posters.append({'name': name, 'gender': gender, 'age': age, 'seat': i})
            j += 1
        string += """<div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Name"""
        for i in names:
            string += """<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(i) + """</h6></div>"""
        string += """<div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Age"""
        for i in ages:
            string += """<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(i) + """</h6></div>"""
        string += """<div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Gender"""
        for i in genders:
            string += """<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(i) + """</h6></div>"""
        string += """<div style=" float: left;
        padding: 5px;
        min-width: 83px;
        text-align: center;
        margin: 8px;">Seat"""
        for i in seat:
            string += """<h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">""" + str(i) + """</h6></div>"""

        string += '''<div style="border-top: 1px solid rgba(51, 51, 51, 0.3); padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;"><h6 style="padding-left: 115px;
        margin: 10px 0px;
        font-size: 15px;">Total : <p>''' + str(
            price) + '''</p></h6></div></div></div></body></html>'''
        send_mail("Ticket Confirmation", string, "yourbusdjango@gmail.com", [request.session.get('Email')],
                  fail_silently=True, html_message=string)
        return render(request, template_name='ticket.html', context={
            'tickets': posters,
            'bus_no': bus.number,
            'title': 'Ticket Info',
            'date': str(str(sday) + '-' + str(smonth) + '-' + str(syear)),
            'source': src.name,
            'dest': dest.name,
            'price': price,
            'arrival': arrival,
            'depart': depart,

        })


class cancel_ticket(ListView):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request):
        pass



class get_bookings(ListView):

    def get(self,request,*args,**kwargs):
        x=Ticket.objects.all()

        user=request.user.pk
        print(user)
        pass

    def post(self,request):
        pass