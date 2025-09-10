from django.contrib import admin
from users.models import UserDetail

#admin.site.register(Users)

@admin.register(UserDetail)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('get_username','get_id')


    def get_username(self, obj):
        return obj.user.username
    def get_id(self, obj):
        return obj.user.id

  



