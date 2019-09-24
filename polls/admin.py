from django.contrib import admin

# Register your models here.
from .models import Question, Choice

class ChoiceInLine(admin.TabularInline): #StackedInLine
    model = Choice
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['question_text']}),
        ('Date Information',    {'fields': ['pub_date'], 'classes':['collapse']}),
    ]
    inlines = [ChoiceInLine]
    list_display = ('question_text', 'pub_date', 'was_published_recently', 'how_many_choices_has')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    list_per_page = 10

admin.site.register(Question, QuestionAdmin)