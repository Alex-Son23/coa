from django.contrib import admin
from .models import *

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username')
    search_fields = ('email', 'username')

admin.site.register(CustomUser, CustomUserAdmin)

class UserRegAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'email', 'birthdate', 'is_approved')
    search_fields = ('username', 'phone_number', 'user__email')
    list_filter = ('is_approved', 'gender', 'education')

    def email(self, obj):
        return obj.user.email

admin.site.register(UserReg, UserRegAdmin)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'topic', 'actual')
    list_filter = ('category', 'topic', 'actual')
    search_fields = ('content',)

admin.site.register(Course, CourseAdmin)

class CourseTimeToBeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'price')

admin.site.register(CourseTimeToBeat, CourseTimeToBeatAdmin)

class CourseExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course')
    list_filter = ('id', 'pdf_file', 'course')

admin.site.register(CourseExercise, CourseExerciseAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

admin.site.register(Topic, TopicAdmin)



admin.site.register(Term_of_study)

admin.site.register(Test)
admin.site.register(Question)

admin.site.register(CourseGrade)
