from statistics import mode
from django.db import models
from django.core import serializers
import moviepy.editor
from django.core.mail import send_mail


# Teacher Model
class Teacher(models.Model):
    full_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100,blank=True,null=True)
    qualification=models.CharField(max_length=200)
    mobile_no=models.CharField(max_length=20)
    profile_img=models.ImageField(upload_to='teacher_profile_imgs/',null=True)
    skills=models.TextField()
    verify_status=models.BooleanField(default=False)
    otp_digit=models.CharField(max_length=10,null=True)
    login_via_otp=models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "1. Teachers"

    def skill_list(self):
        skill_list=self.skills.split(',')
        return skill_list
    
    #Total Teacher Courses
    def total_teacher_courses(self):
        total_courses=Course.objects.filter(teacher=self).count()
        return total_courses
    
    #Total Teacher Chapters
    def total_teacher_chapters(self):
        total_chapters=Chapter.objects.filter(course__teacher=self).count()
        return total_chapters
    
    #Total Teacher Students
    def total_teacher_students(self):
        total_students=StudentCourseEnrollment.objects.filter(course__teacher=self).count()
        return total_students


# Course Category Model
class CourseCategory(models.Model):
    title=models.CharField(max_length=150)
    description=models.TextField()

    class Meta:
        verbose_name_plural = "2. Course Categories"

    # Total course of this category
    def total_courses(self):
        return Course.objects.filter(category=self).count()

        
    def __str__(self) :
        return self.title


# Course Model
class Course(models.Model):
    category=models.ForeignKey(CourseCategory, on_delete=models.CASCADE,related_name='category_courses')
    teacher=models.ForeignKey(Teacher, on_delete=models.CASCADE,related_name='teacher_courses')
    title=models.CharField(max_length=150)
    description=models.TextField()
    featured_img=models.ImageField(upload_to='course_imgs/',null=True)
    techs=models.TextField(null=True)
    course_views=models.BigIntegerField(default=0)

    class Meta:
        verbose_name_plural = "3. Courses"

    def related_videos(self):
        related_videos=Course.objects.filter(techs__icontains=self.techs).exclude(id=self.id)
        return serializers.serialize('json',related_videos)
    
    def tech_list(self):
        tech_list=self.techs.split(',')
        return tech_list
    
    def total_enrolled_students(self):
        total_enrolled_students=StudentCourseEnrollment.objects.filter(course=self).count()
        return total_enrolled_students
    
    def course_rating(self):
        course_rating=CourseRating.objects.filter(course=self).aggregate(avg_rating=models.Avg('rating'))
        return course_rating['avg_rating']
    
    def __str__(self) :
        return self.title

# Chapter Model
class Chapter(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE,related_name='course_chapters')
    title=models.CharField(max_length=150)
    description=models.TextField()
    video=models.FileField(upload_to='chapter_videos/',null=True)
    chapter_duration=models.TextField()
    remarks=models.TextField(null=True)

    class Meta:
        verbose_name_plural = "4. Chapters"

    def chapter_duration(Self):
        seconds=0
        import cv2
        cap = cv2.VideoCapture(Self.video.path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count:
            duration = frame_count/fps
            print('fps = '+ str(fps))
            print('number of frames = ' + str(frame_count))
            print('duration (S) = ' + str(duration))
            minutes = int(duration/60)
            seconds = duration%60
            print('duration (M:S) = '+ str(minutes) + ':' + str(seconds))
        return seconds


# Student Model
class Student(models.Model):
    full_name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    username=models.CharField(max_length=200)
    password=models.CharField(max_length=100,blank=True,null=True)
    referral_code=models.CharField(max_length=20,unique=True)
    interested_categories=models.TextField()
    profile_img=models.ImageField(upload_to='student_profile_imgs/',null=True)
    verify_status=models.BooleanField(default=False)
    otp_digit=models.CharField(max_length=10,null=True)
    login_via_otp=models.BooleanField(default=False)

    def __str__(self) :
        return self.full_name
    
    #Total Enrolled Courses
    def enrolled_courses(self):
        enrolled_courses=StudentCourseEnrollment.objects.filter(student=self).count()
        return enrolled_courses
    
    #Total Favourite Courses
    def favourite_courses(self):
        favourite_courses=StudentFavouriteCourse.objects.filter(student=self).count()
        return favourite_courses
    
    #Completed Assignments
    def complete_assignments(self):
        complete_assignments=StudentAssignment.objects.filter(student=self,student_status=True).count()
        return complete_assignments
    
    #Pending Assignments
    def pending_assignments(self):
        pending_assignments=StudentAssignment.objects.filter(student=self,student_status=False).count()
        return pending_assignments

    class Meta:
        verbose_name_plural = "5. Students"


# Student Course Enrollment
class StudentCourseEnrollment(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='enrolled_courses')
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='enrolled_student')
    enrolled_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="6. Enrolled Courses"

    def __str__(self) :
        return f"{self.course}-{self.student}"
    
# Student Favourite Course
class StudentFavouriteCourse(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    status=models.BooleanField(default=False)

    class Meta:
        verbose_name_plural="7. Student Favourite Courses"

    def __str__(self) :
        return f"{self.course}-{self.student}"
    
# Course Rating and Reviews
class CourseRating(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=True)
    student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True)
    rating=models.PositiveBigIntegerField(default=0)
    reviews=models.TextField(null=True)
    review_time=models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return f"{self.course}-{self.student}-{self.rating}"
    
    class Meta:
        verbose_name_plural="8. Course Ratings"

# Student Assignments
class StudentAssignment(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True)
    student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True)
    title=models.CharField(max_length=100)
    detail=models.TextField(null=True)
    student_status=models.BooleanField(default=False,null=True)
    add_time=models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return f"{self.title}"
    
    class Meta:
        verbose_name_plural="9. Student Assignments"

# Notification Model
class Notification(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True)
    student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True)
    notif_subject=models.CharField(max_length=200,verbose_name='Notification Subject',null=True)
    notif_for=models.CharField(max_length=200,verbose_name='Notification For')
    notif_created_time=models.DateTimeField(auto_now_add=True)
    notifiread_status=models.BooleanField(default=False,verbose_name='Notification Status')

    # def __str__(self):
    #     return self.title

    class Meta:
        verbose_name_plural="10. Notifications"

# Quiz Model
class Quiz(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True)
    title=models.CharField(max_length=200)
    detail=models.TextField()
    add_time=models.DateTimeField(auto_now_add=True)

    def assign_status(self):
        return models.CourseQuiz.objects.filter(quiz=self).count()

    class Meta:
        verbose_name_plural="11. Quiz"

# Quiz Questions MOdel
class QuizQuestions(models.Model):
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,null=True)
    questions=models.CharField(max_length=200)
    answer1=models.CharField(max_length=200)
    answer2=models.CharField(max_length=200)
    answer3=models.CharField(max_length=200)
    answer4=models.CharField(max_length=200)
    right_answer=models.CharField(max_length=200)
    add_time=models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural="12. Quiz Questions"

# Add Quiz to Course
class CourseQuiz(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True)
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=True)
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,null=True)
    add_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="13. Course Quiz"

# Attempt Quiz Ques by Stu
class AttemptQuiz(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True)
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,null=True)
    question=models.ForeignKey(QuizQuestions,on_delete=models.CASCADE,null=True)
    right_answer=models.CharField(max_length=200,null=True)
    add_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="14. Attempted Questions"

# Study Material Model
class StudyMaterial(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE)
    title=models.CharField(max_length=150)
    description=models.TextField()
    upload=models.FileField(upload_to='study_materials/',null=True)
    remarks=models.TextField(null=True)

    class Meta:
        verbose_name_plural = "15. Course Study Materials"

# FAQ Model
class FAQ(models.Model):
    question=models.CharField(max_length=500)
    answer=models.TextField()

    def __str__(self) -> str:
        return self.question

    class Meta:
        verbose_name_plural = "16. FAQ"

# Contact Us Model
class Contact(models.Model):
    full_name=models.CharField(max_length=100)
    email=models.EmailField()
    query_txt=models.TextField()
    add_time=models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.query_txt
    
    def save(self,*args,**kwargs):
        send_mail(
            "Contact Query",
            "Here is the message.",
            "shikshakendra@gmail.com",
            [self.email],
            fail_silently=False,
            html_message=f'<p>{self.full_name}</p><p>{self.query_txt}</p>'
        )
        return super(Contact,self).save(*args,**kwargs)

    class Meta:
        verbose_name_plural = "17. Contact Queries"

    