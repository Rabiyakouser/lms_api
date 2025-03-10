from webbrowser import get
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
# from rest_framework.views import APIView
from django.db.models import Q,Count,Avg,F
from django.contrib.flatpages.models import FlatPage
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from django.core.mail import send_mail

from .serializers import TeacherSerializer,CategorySerializer,CourseSerializer,ChapterSerializer,StudentSerializer, StudentCourseEnrollSerializer,TeacherDashboardSerializer,CourseRatingSerializer,StudentFavouriteCourseSerializer,StudentAssignmentSerializer,StudentDashboardSerializer,NotificationSerializer,QuizSerializer,QuestionSerializer,CourseQuizSerializer,AttemptQuizSerializer,StudyMaterialSerializer,FaqSerializer,FlatPagesSerializer,ContactSerializer
from .import models

from random import randint


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 8

class TeacherList(generics.ListCreateAPIView):
    queryset = models.Teacher.objects.all()
    serializer_class = TeacherSerializer
    
    def get_queryset(self):
        if 'popular' in self.request.GET:
          sql="SELECT *,COUNT(c.id) as total_course FROM main_teacher as t INNER JOIN main_course as c ON c.teacher_id=t.id GROUP BY t.id ORDER BY total_course desc"
          return models.Teacher.objects.raw(sql)
            

class TeacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Teacher.objects.all()
    serializer_class = TeacherSerializer
    # permission_classes = [permissions.IsAuthenticated]

class TeacherDashboard(generics.RetrieveAPIView):
    queryset = models.Teacher.objects.all()
    serializer_class = TeacherDashboardSerializer

@csrf_exempt
def teacher_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        teacherData=models.Teacher.objects.get(email=email,password=password)
    except models.Teacher.DoesNotExist:
        teacherData=None
    if teacherData:
        if not teacherData.verify_status:
            return JsonResponse({'bool':False,'teacher_id':teacherData.id,'msg':'Account is not verified!!'})
        else:
            if teacherData.login_via_otp:
                # Send OTP Email
                otp_digit=randint(100000,999999)
                send_mail(
                    "Verify Account",
                    "Please verify your account",
                    "shikshakendra@gmail.com",
                    [teacherData.email],
                    fail_silently=False,
                    html_message=f'<p>Your OTP is</p><p>{otp_digit}</p>'
                )
                teacherData.otp_digit=otp_digit
                teacherData.save()
                return JsonResponse({'bool':True,'teacher_id':teacherData.id,'login_via_otp':True})
            else:
                 return JsonResponse({'bool':True,'teacher_id':teacherData.id,'login_via_otp':False})
    else:
       return JsonResponse({'bool':False,'msg':'Invalid Email Or Password!!'})

@csrf_exempt
def verify_teacher_via_otp(request,teacher_id):
    otp_digit=request.POST.get('otp_digit')
    verify=models.Teacher.objects.filter(id=teacher_id,otp_digit=otp_digit).first()
    if verify:
        models.Teacher.objects.filter(id=teacher_id,otp_digit=otp_digit).update(verify_status=True)
        return JsonResponse({'bool':True,'teacher_id':verify.id})
    else:
        return JsonResponse({'bool':False,'msg':'Please enter valid 6 digit OTP'})

    
class CategoryList(generics.ListCreateAPIView):
    queryset = models.CourseCategory.objects.all()
    serializer_class = CategorySerializer
    

# course
class CourseList(generics.ListCreateAPIView):
    queryset = models.Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class=StandardResultsSetPagination

    def get_queryset(self):
        qs=super().get_queryset()
        if 'result' in self.request.GET:
            limit=int(self.request.GET['result'])
        #     qs=models.CourseRating.objects.all().order_by('-course_rating')[:limit]
        # else:
            qs=models.Course.objects.all().order_by('-id')[:limit]
    
        if 'category' in self.request.GET:
            category=self.request.GET['category']
            category=models.CourseCategory.objects.filter(id=category).first()
            qs=models.Course.objects.filter(category=category)
        
    
        if 'skill_name' in self.request.GET and  'teacher' in self.request.GET:
            skill_name=self.request.GET['skill_name']
            teacher=self.request.GET['teacher']
            teacher=models.Teacher.objects.filter(id=teacher).first()
            qs=models.Course.objects.filter(techs__icontains=skill_name,teacher=teacher)

        if 'searchstring' in self.kwargs:
            search=self.kwargs['searchstring']
            if search:
                qs=models.Course.objects.filter(Q(title__icontains=search)|Q(techs__icontains=search))
    
        elif 'studentId' in self.kwargs:
            student_id=self.kwargs['studentId']
            student=models.Student.objects.get(pk=student_id)
            print(student.interested_categories)
            queries = [Q(techs__iendswith=value) for value in student.interested_categories]
            query = queries.pop()
            for item in queries:
                query |= item
            qs=models.Course.objects.filter(query)
            return qs
        
        return qs
    
class CourseDetailView(generics.RetrieveAPIView):
    queryset=models.Course.objects.all()
    serializer_class=CourseSerializer

# specific teacher course
class TeacherCourseList(generics.ListCreateAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        teacher_id=self.kwargs['teacher_id']
        teacher=models.Teacher.objects.get(pk=teacher_id)
        return models.Course.objects.filter(teacher=teacher)
    
# specific teacher course
class TeacherCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Course.objects.all()
    serializer_class = CourseSerializer
    
# chapter
class ChapterList(generics.ListCreateAPIView):
    queryset = models.Chapter.objects.all()
    serializer_class = ChapterSerializer

class CourseChapterList(generics.ListCreateAPIView):
    serializer_class = ChapterSerializer

    def get_queryset(self):
        course_id=self.kwargs['course_id']
        course=models.Course.objects.get(pk=course_id)
        return models.Chapter.objects.filter(course=course)
    
class ChapterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Chapter.objects.all()
    serializer_class=ChapterSerializer

    def get_serializer_context(self):
        context=super().get_serializer_context()
        context['chapter_duration']=self.chapter_duration
        print('context------------')
        print(context)
        return context
    
# Student Data 
class StudentList(generics.ListCreateAPIView):
    queryset = models.Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = [permissions.IsAuthenticated]

class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Student.objects.all()
    serializer_class =StudentSerializer
    # permission_classes = [permissions.IsAuthenticated]

class StudentDashboard(generics.RetrieveAPIView):
    queryset = models.Student.objects.all()
    serializer_class = StudentDashboardSerializer

@csrf_exempt
def student_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        studentData=models.Student.objects.get(email=email,password=password)
    except models.Student.DoesNotExist:
        studentData=None
    if studentData:
        if not studentData.verify_status:
            return JsonResponse({'bool':False, 'msg':'Account is not verified!!'})
        else:
            if studentData.login_via_otp:
                # Send OTP Email
                otp_digit=randint(100000,999999)
                send_mail(
                    "Verify Account",
                    "Please verify your account",
                    "shikshakendra@gmail.com",
                    [studentData.email],
                    fail_silently=False,
                    html_message=f'<p>Your OTP is</p><p>{otp_digit}</p>'
                )
                studentData.otp_digit=otp_digit
                studentData.save()
                return JsonResponse({'bool':True,'student_id':studentData.id,'login_via_otp':True})
            else:
                 return JsonResponse({'bool':True,'student_id':studentData.id,'login_via_otp':False})
    else:
       return JsonResponse({'bool':False,'msg':'Invalid Email Or Password!!'})
    

@csrf_exempt
def verify_student_via_otp(request,student_id):
    otp_digit=request.POST.get('otp_digit')
    verify=models.Student.objects.filter(id=student_id,otp_digit=otp_digit).first()
    if verify:
        models.Student.objects.filter(id=student_id,otp_digit=otp_digit).update(verify_status=True)
        return JsonResponse({'bool':True,'student_id':verify.id})
    else:
        return JsonResponse({'bool':False})
    
class StudentEnrollCourseList(generics.ListCreateAPIView):
     queryset = models.StudentCourseEnrollment.objects.all()
     serializer_class = StudentCourseEnrollSerializer

class StudentFavouriteCourseList(generics.ListCreateAPIView):
     queryset = models.StudentFavouriteCourse.objects.all()
     serializer_class = StudentFavouriteCourseSerializer

def get_queryset(self):
        if 'student_id' in self.kwargs:
            student_id=self.kwargs['student_id']
            student=models.Student.objects.get(pk=student_id)
            return models.StudentFavouriteCourse.objects.filter(student=student).distinct()

def fetch_enroll_status(request,student_id,course_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    enrollStatus=models.StudentCourseEnrollment.objects.filter(course=course,student=student).count()
    if enrollStatus:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})
    

def fetch_favourite_status(request,student_id,course_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    favouriteStatus=models.StudentFavouriteCourse.objects.filter(course=course,student=student).first()
    if favouriteStatus and favouriteStatus.status == True:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})
    
def remove_favourite_status(course_id,student_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    favouriteStatus=models.StudentFavouriteCourse.objects.filter(course=course,student=student).first()
    if favouriteStatus and favouriteStatus.status == True:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})



def fetch_enroll_status(request,student_id,course_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    favouriteStatus=models.StudentFavouriteCourse.objects.filter(course=course,student=student).delete()
    if favouriteStatus:
        return JsonResponse({'bool':True})
    else:
       return JsonResponse({'bool':False})
    
class EnrolledStudentList(generics.ListCreateAPIView):
     queryset = models.StudentCourseEnrollment.objects.all()
     serializer_class = StudentCourseEnrollSerializer
   
     def get_queryset(self):
        if 'course_id' in self.kwargs:
            course_id=self.kwargs['course_id']
            course=models.Course.objects.get(pk=course_id)
            return models.StudentCourseEnrollment.objects.filter(course=course)
        elif 'teacher_id' in self.kwargs:
            teacher_id=self.kwargs['course_id']
            teacher=models.Teacher.objects.get(pk=teacher_id)
            return models.StudentCourseEnrollment.objects.filter(course__teacher=teacher).distinct()
        elif 'student_id' in self.kwargs:
            student_id=self.kwargs['student_id']
            student=models.Student.objects.get(pk=student_id)
            return models.StudentCourseEnrollment.objects.filter(student=student).distinct()
        

     
class CourseRatingList(generics.ListCreateAPIView):
     queryset=models.CourseRating.objects.all()
     serializer_class = CourseRatingSerializer

     def get_queryset(self):
         if 'popular' in self.request.GET:
             sql="SELECT *,AVG(cr.rating) as avg_rating FROM main_courserating as cr INNER JOIN main_course as c ON cr.course_id=c.id GROUP BY c.id ORDER BY avg_rating desc LIMIT 1"
             return models.CourseRating.objects.raw(sql)
         if 'all' in self.request.GET:
            sql="SELECT *,AVG(cr.rating) as avg_rating FROM main_courserating as cr INNER JOIN main_course as c ON cr.course_id=c.id GROUP BY c.id ORDER BY avg_rating desc"
            return models.CourseRating.objects.raw(sql)
         return models.CourseRating.objects.filter(course__isnull=False).order_by('-rating')

def fetch_rating_status(request,student_id,course_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    ratingStatus=models.CourseRating.objects.filter(course=course,student=student).count()
    if ratingStatus:
        return JsonResponse({'bool':True})
    else:
       return JsonResponse({'bool':False})
    

@csrf_exempt
def teacher_change_password(request,teacher_id):
    password=request.POST['password']
    try:
        teacherData=models.Teacher.objects.get(id=teacher_id)
    except models.Teacher.DoesNotExist:
        teacherData=None
    if teacherData:
        models.Teacher.objects.filter(id=teacher_id).update(password=password)
        return JsonResponse({'bool':True})
    else:
       return JsonResponse({'bool':False})
    
class AssignmentList(generics.ListCreateAPIView):
    queryset = models.StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer

    def get_queryset(self):
        student_id=self.kwargs['student_id']
        teacher_id=self.kwargs['teacher_id']
        student=models.Student.objects.get(pk=student_id)
        teacher=models.Teacher.objects.get(pk=teacher_id)
        return models.StudentAssignment.objects.filter(student=student, teacher=teacher)
    
class MyAssignmentList(generics.ListCreateAPIView):
    queryset = models.StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer

    def get_queryset(self):
        student_id=self.kwargs['student_id']
        student=models.Student.objects.get(pk=student_id)
        #Update Notifications
        models.Notification.objects.filter(student=student,notif_for='student',notif_subject='assignment').update(notifiread_status=True)
        return models.StudentAssignment.objects.filter(student=student)
    
class UpdateAssignment(generics.RetrieveDestroyAPIView):
    queryset = models.StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer

@csrf_exempt
def student_change_password(request,student_id):
    password=request.POST['password']
    try:
        studentData=models.Student.objects.get(id=student_id)
    except models.Teacher.DoesNotExist:
        studentData=None
    if studentData:
        models.Student.objects.filter(id=student_id).update(password=password)
        return JsonResponse({'bool':True})
    else:
       return JsonResponse({'bool':False})
    
class NotificationList(generics.ListCreateAPIView):
    queryset=models.Notification.objects.all()
    serializer_class=NotificationSerializer

    def get_queryset(self):
        student_id=self.kwargs['student_id']
        student=models.Student.objects.get(pk=student_id)
        return models.Notification.objects.filter(student=student,notif_for='student',notif_subject='assignment',notifiread_status=False)
    
class QuizList(generics.ListCreateAPIView):
    queryset=models.Quiz.objects.all()
    serializer_class=QuizSerializer

class TeacherQuizList(generics.ListCreateAPIView):
    serializer_class = QuizSerializer

    def get_queryset(self):
        teacher_id=self.kwargs['teacher_id']
        teacher=models.Teacher.objects.get(pk=teacher_id)
        return models.Quiz.objects.filter(teacher=teacher)
    
class TeacherQuizDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Quiz.objects.all()
    serializer_class = QuizSerializer

class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.Quiz.objects.all()
    serializer_class = QuizSerializer

class QuizQuestionList(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz_id=self.kwargs['quiz_id']
        quiz=models.Quiz.objects.get(pk=quiz_id)
        if 'limit' in self.kwargs:
            return models.QuizQuestions.objects.filter(quiz=quiz).order_by('id')[:1]
        elif 'question_id' in self.kwargs:
            current_question=self.kwargs['question_id']
            return models.QuizQuestions.objects.filter(quiz=quiz,id__gt=current_question).order_by('id')[:1]
        else:
            return models.QuizQuestions.objects.filter(quiz=quiz)
    
class CourseQuizList(generics.ListCreateAPIView):
     queryset = models.CourseQuiz.objects.all()
     serializer_class =  CourseQuizSerializer

     def get_queryset(self):
         if 'course_id' in self.kwargs:
             course_id=self.kwargs['course_id']
             course = models.Course.objects.get(pk=course_id)
             return models.CourseQuiz.objects.filter(course=course)


def fetch_quiz_assign_status(request,quiz_id,course_id):
    quiz=models.Quiz.objects.filter(id=quiz_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    assignStatus=models.CourseQuiz.objects.filter(course=course,quiz=quiz).count()
    if assignStatus:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})
    
class AttemptQuizList(generics.ListCreateAPIView):
    queryset=models.AttemptQuiz.objects.all()
    serializer_class=AttemptQuizSerializer

    def get_queryset(self):
        if 'quiz_id' in self.kwargs:
            quiz_id=self.kwargs['quiz_id']
            quiz = models.Quiz.objects.get(pk=quiz_id)
            # return models.AttemptQuiz.objects.filter(quiz=quiz)
            return models.AttemptQuiz.objects.raw(f'SELECT * FROM main_attemptquiz WHERE quiz_id={int(quiz_id)} GROUP BY student_id')


def fetch_quiz_attempt_status(request,quiz_id,student_id):
    quiz=models.Quiz.objects.filter(id=quiz_id).first()
    student=models.Student.objects.filter(id=student_id).first()
    attemptStatus=models.AttemptQuiz.objects.filter(student=student,question__quiz=quiz).count()
    print(models.AttemptQuiz.objects.filter(student=student,question__quiz=quiz).query)
    if attemptStatus > 0:
        return JsonResponse({'bool':True})
    else:
        return JsonResponse({'bool':False})
    
def fetch_quiz_result(request,quiz_id,student_id):
    quiz = models.Quiz.objects.filter(id=quiz_id).first()
    student = models.Student.objects.filter(id=student_id).first()
    total_questions=models.QuizQuestions.objects.filter(quiz=quiz).count()
    total_attempted_questions=models.AttemptQuiz.objects.filter(quiz=quiz,student=student).values('student').count()
    attempted_questions=models.AttemptQuiz.objects.filter(quiz=quiz,student=student)

    total_correct_questions=0
    for attempt in attempted_questions:
        if attempt.right_answer == attempt.question.right_answer:
            total_correct_questions+=1
            
    return JsonResponse({'total_questions':total_questions,'total_attempted_questions':total_attempted_questions,'total_correct_questions':total_correct_questions})
    
class StudyMaterialList(generics.ListCreateAPIView):
    serializer_class = StudyMaterialSerializer

    def get_queryset(self):
        course_id=self.kwargs['course_id']
        course=models.Course.objects.get(pk=course_id)
        return models.StudyMaterial.objects.filter(course=course)
    
class StudyMaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=models.StudyMaterial.objects.all()
    serializer_class=StudyMaterialSerializer

def update_view(request,course_id):
    queryset=models.Course.objects.filter(pk=course_id).first()
    queryset.course_views+=1
    queryset.save()
    return JsonResponse({'views':queryset.course_views})

def fetch_student_testimonial(request,quiz_id,student_id):
    quiz=models.Quiz.objects.filter(id=quiz_id).first()
    student=models.Student.objects.filter(id=student_id).first()
    total_questions=models.QuizQuestions.objects.filter(quiz=quiz).count()
    total_attempted_questions=models.AttemptQuiz.objects.filter(quiz=quiz,student=student).values('student').count()
    return JsonResponse({'total_questions':total_questions,'total_attempted_questions':total_attempted_questions})

class FaqList(generics.ListAPIView):
    queryset = models.FAQ.objects.all()
    serializer_class = FaqSerializer

class FlatPagesList(generics.ListAPIView):
    queryset= FlatPage.objects.all()
    serializer_class=FlatPagesSerializer


class FlatPagesDetail(generics.RetrieveAPIView):
    queryset= FlatPage.objects.all()
    serializer_class=FlatPagesSerializer

class ContactList(generics.ListCreateAPIView):
    queryset = models.Contact.objects.all()
    serializer_class = ContactSerializer


@csrf_exempt
def teacher_forgot_password(request):
    email=request.POST.get('email')
    verify=models.Teacher.objects.filter(email=email).first()
    if verify:
        link=f"http://localhost:3000/teacher-change-password/{verify.id}/"
        send_mail(
                    "Verify Account",
                    "Please verify your account",
                    "shikshakendra@gmail.com",
                    [email],
                    fail_silently=False,
                    html_message=f'<p>Your OTP is</p><p>{link}</p>'
                )
        return JsonResponse({'bool':True,'msg':'Please Check Your Email'})
    else:
        return JsonResponse({'bool':False,'msg':'Invalid Email!!'})
    
@csrf_exempt
def teacher_change_password(request,teacher_id):
    password=request.POST.get('password')
    verify=models.Teacher.objects.filter(id=teacher_id).first()
    if verify:
        models.Teacher.objects.filter(id=teacher_id).update(password=password)
        return JsonResponse({'bool':True,'msg':'Password has been changed'})
    else:
        return JsonResponse({'bool':False,'msg':'Oops...Some Error Occurred'})
    

@csrf_exempt
def user_forgot_password(request):
    email=request.POST.get('email')
    verify=models.Student.objects.filter(email=email).first()
    if verify:
        link=f"http://localhost:3000/user-change-password/{verify.id}/"
        send_mail(
                    "Verify Account",
                    "Please verify your account",
                    "shikshakendra@gmail.com",
                    [email],
                    fail_silently=False,
                    html_message=f'<p>Your OTP is</p><p>{link}</p>'
                )
        return JsonResponse({'bool':True,'msg':'Please Check Your Email'})
    else:
        return JsonResponse({'bool':False,'msg':'Invalid Email!!'})
    
@csrf_exempt
def user_change_password(request,student_id):
    password=request.POST.get('password')
    verify=models.Student.objects.filter(id=student_id).first()
    if verify:
        models.Student.objects.filter(id=student_id).update(password=password)
        return JsonResponse({'bool':True,'msg':'Password has been changed'})
    else:
        return JsonResponse({'bool':False,'msg':'Oops...Some Error Occurred'})

