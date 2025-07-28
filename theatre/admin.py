from django.contrib import admin

from .models import Play, Genre, TheatreHall, Ticket, Reservation, Actor, Performance

admin.site.register(Play)
admin.site.register(Genre)
admin.site.register(TheatreHall)
admin.site.register(Ticket)
admin.site.register(Reservation)
admin.site.register(Actor)
admin.site.register(Performance)
