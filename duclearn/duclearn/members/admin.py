from django.contrib import admin
from .models import Memeber

# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "joined_date",)

admin.site.register(Memeber, MemberAdmin)



