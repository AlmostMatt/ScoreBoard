from django.contrib import admin
from tsw.models import User, HighScore

from django.contrib.admin.filters import AllValuesFieldListFilter

class DropDownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class HighScoreAdmin(admin.ModelAdmin):
    fields = ['user', 'level', 'score', 'score_date']
    list_display = ('level', 'user', 'score', 'score_date')
    list_filter = [('level', DropDownFilter), 'score_date', 'user']

admin.site.register(User, UserAdmin)
admin.site.register(HighScore, HighScoreAdmin)
