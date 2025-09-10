from django.contrib import admin

from families.models import Family
from familymember.models import FamilyMember



# Register your models here.


@admin.register(Family)
class FamiliesAdmin(admin.ModelAdmin):
    list_display = ('family_id','name','member_count')

    def member_count(self, obj):
        return obj.familymember_set.count() 
    member_count.short_description = 'Members Count'





