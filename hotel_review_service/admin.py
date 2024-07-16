from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import HotelClass, Hotel, Placement, User, Review


admin.site.register(Hotel)
admin.site.register(HotelClass)
admin.site.register(Placement)
admin.site.register(Review)
admin.site.register(User, UserAdmin)
