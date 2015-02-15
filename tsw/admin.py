from django.contrib import admin
from tsw.models import User, HighScore, CustomLevel

from django.contrib.admin.filters import AllValuesFieldListFilter

class DropDownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']

class HighScoreAdmin(admin.ModelAdmin):
    fields = ['user', 'level', 'score', 'score_date']
    list_display = ('level', 'user', 'score', 'score_date')
    list_filter = [('level', DropDownFilter), 'score_date', ('user__id', DropDownFilter)]
    search_fields = ['user__name']

class CustomLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'level_name', 'creator', 'create_date')
    #fields = ['creator', 'level_name', 'create_date', 'plays', 'completions', 'ratings', 'total_rating', 'avg_rating']
    list_filter = [('creator__id', DropDownFilter), 'create_date']
    search_fields = ['creator__name', 'level_name']

admin.site.register(User, UserAdmin)
admin.site.register(HighScore, HighScoreAdmin)
admin.site.register(CustomLevel, CustomLevelAdmin)
