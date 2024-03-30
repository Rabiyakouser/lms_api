from django.contrib import admin
from . import models

admin.site.register(models.Teacher)
admin.site.register(models.CourseCategory)
admin.site.register(models.Course)
admin.site.register(models.Chapter)
admin.site.register(models.Student)
admin.site.register(models.StudentCourseEnrollment)
admin.site.register(models.CourseRating)
admin.site.register(models.StudentFavouriteCourse)
admin.site.register(models.StudentAssignment)

class NotificationAdmin(admin.ModelAdmin):
    list_display=['id','notif_subject','notif_for','notifiread_status']
admin.site.register(models.Notification,NotificationAdmin)

admin.site.register(models.Quiz)
admin.site.register(models.QuizQuestions)
admin.site.register(models.CourseQuiz)
admin.site.register(models.AttemptQuiz)
admin.site.register(models.StudyMaterial)
admin.site.register(models.FAQ)
