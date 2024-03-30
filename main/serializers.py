from rest_framework import serializers
from rest_framework.response import Response
from . import models
from django.contrib.flatpages.models import FlatPage
from django.core.mail import send_mail

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ['id','full_name','email','password','qualification','mobile_no','skills','otp_digit','login_via_otp','profile_img','teacher_courses','skill_list','total_teacher_courses']
        # depth=1

    
    def __init__(self,*args,**kwargs):
        super(TeacherSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=1

    def create(self,validate_data):
        email=self.validated_data['email']
        otp_digit=self.validated_data['otp_digit']
        instance = super(TeacherSerializer, self).create(validate_data)
        send_mail(
            "Verify Account",
            "Please verify your account",
            "shikshakendra@gmail.com",
            [email],
            fail_silently=False,
            html_message=f'<p>Your OTP is</p><p>{self.otp_digit}</p>'
        )
        return instance

class TeacherDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Teacher
        fields=['total_teacher_courses','total_teacher_students','total_teacher_chapters']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseCategory
        fields = ['id','title','description','total_courses']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id','category','teacher','title','description','featured_img','techs','course_chapters','related_videos','tech_list','total_enrolled_students','course_rating']
        # depth=1

    def __init__(self,*args,**kwargs):
        super(CourseSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=1

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chapter
        fields = ['id','course','title','description','video','chapter_duration','remarks']

    def __init__(self,*args,**kwargs):
        super(ChapterSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=1

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = ['id','full_name','email','user_name','login_via_otp','password','referral_code','interested_categories','otp_digit','profile_img']

    def create(self,validate_data):
        email=self.validated_data['email']
        otp_digit=self.validated_data['otp_digit']
        instance = super(StudentSerializer, self).create(validate_data)
        send_mail(
            "Verify Account",
            "Please verify your account",
            "shikshakendra@gmail.com",
            [email],
            fail_silently=False,
            html_message=f'<p>Your OTP is</p><p>{self.otp_digit}</p>'
        )
        return instance

    
    def __init__(self,*args,**kwargs):
        super(StudentSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=2


class StudentCourseEnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.StudentCourseEnrollment
        fields=['id','course','student','enrolled_time']
    

    def __init__(self,*args,**kwargs):
        super(StudentCourseEnrollSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=2

class StudentFavouriteCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.StudentFavouriteCourse
        fields=['id','course','student','status']
    

    def __init__(self,*args,**kwargs):
        super(StudentFavouriteCourseSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=2

class CourseRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseRating
        fields = ['id','course','student','rating','reviews','review_time']
        # depth=1

    def __init__(self,*args,**kwargs):
        super(CourseRatingSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=2

class StudentAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAssignment
        fields = ['id','teacher','student','title','detail','student_status','add_time']
        # depth=1

    def __init__(self,*args,**kwargs):
        super(StudentAssignmentSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=2

class StudentDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Student
        fields=['enrolled_courses','favourite_courses','complete_assignments','pending_assignments']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Notification
        fields=['teacher','student','notif_subject','notif_for']

    def __init__(self,*args,**kwargs):
        super(NotificationSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth = 2

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Quiz
        fields = ['id','teacher','title','detail','assign_status','add_time']

    def __init__(self,*args,**kwargs):
        super(QuizSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=1

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuizQuestions
        fields = ['id','quiz','questions','answer1','answer2','answer3','answer4','right_answer']

    def __init__(self,*args,**kwargs):
        super(QuestionSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=1

class CourseQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.CourseQuiz
        fields=['id','teacher','course','quiz','add_time']
    

    def __init__(self,*args,**kwargs):
        super(CourseQuizSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=2

class AttemptQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.CourseQuiz
        fields=['id','student','question','right_answer','add_time']
    

    def __init__(self,*args,**kwargs):
        super(AttemptQuizSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=2

class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudyMaterial
        fields = ['id','course','title','description','upload','remarks']

    def __init__(self,*args,**kwargs):
        super(StudyMaterialSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        self.Meta.depth = 0
        if request and request.method == 'GET':
            self.Meta.depth=1

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.FAQ
        fields=['question','answer']

class FlatPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model=FlatPage
        fields=['id','title','content','url']
    

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Contact
        fields=['id','full_name','email','query_txt']
    

    