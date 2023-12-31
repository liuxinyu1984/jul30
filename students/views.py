from typing import Any, Dict
from django.db import models
from django.shortcuts import render, redirect
from courses.models import Course, Lecture
from .models import Enrollment
from videos.models import VimeoVideo
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CreateEnrollmentForm
from django.contrib.auth.decorators import login_required
import vimeo, requests, json
#from videos.vimeo_key import *
from backend.settings import MAX_WATCH
from backend.settings import VIMEO_CLIENT_IDENTIFIER, VIMEO_PERSONAL_ACCESS_TOKEN, VIMEO_CLIENT_SECRET, VIMEO_USER_ID, uri_user

class AllCourseList(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/all_course_list.html'


class CourseIntroduction(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'students/course_introduction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(pk=self.kwargs['pk'])
        return context

class RegisterCourse(LoginRequiredMixin, CreateView):
    model = Enrollment
    template_name = 'students/register_course.html'
    form_class = CreateEnrollmentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        course = Course.objects.get(pk=self.kwargs['pk'])
        student = self.request.user
        return {'course': course, 'student': student }


class StudentCourseList(LoginRequiredMixin, ListView):
    model = Enrollment
    template_name = 'students/student_course_list.html'

    def get_queryset(self, **kwargs):
        return Enrollment.objects.filter(student=self.request.user)



###########################################
#### student course detail
###########################################

# CBV
class StudentCourseDetail(LoginRequiredMixin, DetailView):
    model = Enrollment
    template_name = 'students/student_course_detail.html'
    pk_url_kwarg = 'enrollment_id'

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)
    
# FBV
@login_required
def student_course_detail(request, enrollment_id):

    template = 'students/student_course_detail.html'
    enrollment = Enrollment.objects.get(pk=enrollment_id)

    if request.user != enrollment.student:
        is_right_student = False
        message = "Warning: You are not enrolled in this course!"
        context = {
            "is_right_student": is_right_student,
            "message": message,
        }
        return render(request, template, context)
    else:
        is_right_student = True
        message = f"Course detail page of {enrollment.course}"
        context = {
            "is_right_student": is_right_student,
            "message": message,
            "enrollment": enrollment
        }
        return render(request, template, context)


###########################################
#### student lecture detail
###########################################

# CBV
class StudentLectureDetail(LoginRequiredMixin, DetailView):
    model = Enrollment
    template_name = 'students/student_lecture_detail.html'
    pk_url_kwarg = 'enrollment_id'

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.activated:
            context['lecture'] = Lecture.objects.get(pk=self.kwargs['lecture_id'])
        return context
    

# FBV
@login_required
def student_lecture_detail(request, enrollment_id, lecture_id):

    template = 'students/student_lecture_detail.html'
    enrollment = Enrollment.objects.get(pk=enrollment_id)
    is_activated = enrollment.activated

    if is_activated:
        lecture = Lecture.objects.get(pk=lecture_id)
    else:
        lecture = None

    if request.user != enrollment.student:
        is_right_student = False
        message = "Warning: You are not enrolled in this course!"
        context = {
            "is_right_student": is_right_student,
            "message": message,
            "enrollment_id": enrollment.id,
            "is_activated": is_activated
        }
        return render(request, template, context)
    else:
        is_right_student = True
        message = f"Lecture detail page of {lecture}"
        context = {
            "is_right_student": is_right_student,
            "message": message,
            "lecture": lecture,
            "enrollment_id": enrollment.id,
            "is_activated": is_activated
        }
        return render(request, template, context)







class PublicLecture(LoginRequiredMixin, DetailView):
    model = Lecture
    template_name = 'students/public_lecture.html'
    pk_url_kwarg = 'lecture_id'

    def get_queryset(self):
        return Lecture.objects.filter(is_public=True)
    

###################################################################
## helper function: send request to vimeo, get player_embed_url
# arg: uri---uri field value from a video object
# return value: (type string) response_json["player_embed_url"]
###################################################################
def player_embed_url(uri):
    client = vimeo.VimeoClient(
                token=VIMEO_PERSONAL_ACCESS_TOKEN,
                key=VIMEO_CLIENT_IDENTIFIER,
                secret=VIMEO_CLIENT_SECRET
            )
    response = client.get(uri)
    response_json = response.json()
    return response_json["player_embed_url"]


@login_required
def student_video_detail(request, enrollment_id, video_id):

    template = 'students/student_video_detail.html'
    enrollment = Enrollment.objects.get(pk=enrollment_id)
    is_activated = enrollment.activated
    nums_watched_dict = enrollment.nums_watched

    video = VimeoVideo.objects.get(pk=video_id)
    max_watch = video.max_num_watch
    uri = video.uri
    key = "video_%d" % video.pk

    if video.lecture.course != enrollment.course:
        return redirect('student_course_detail', enrollment_id)


    if request.user != enrollment.student:
        is_right_student = False
        message = "Warning: You are not enrolled in this course!"
        context = {
            "is_right_student": is_right_student,
            "message": message
        }
    else:
        is_right_student = True
        message = f"Video page of {video}"

        if is_activated:
            if key not in nums_watched_dict:
                new_pair = {key:1}
                nums_watched_dict.update(new_pair)
                enrollment.nums_watched = nums_watched_dict
                enrollment.save(update_fields=["nums_watched"])

                context = {
                    "is_right_student": is_right_student,
                    "is_activated": is_activated,
                    "message": message,
                    "lecture_id": video.lecture.id,
                    "enrollment_id": enrollment.id,
                    "player_embed_url": player_embed_url(uri),
                    "visit_times": enrollment.nums_watched[key]
                }
            else:
                if nums_watched_dict[key] >= video.max_num_watch:
                    message = f"You have watched this video times {video.max_num_watch}"
                    context = {
                        "is_right_student": is_right_student,
                        "is_activated": is_activated,
                        "message": message,
                        "lecture_id": video.lecture.id,
                        "enrollment_id": enrollment.id,
                        "visit_times": enrollment.nums_watched[key],
                        "limit_exceeded": True
                    }
                else:
                    nums_watched_dict[key] +=1
                    enrollment.nums_watched = nums_watched_dict
                    enrollment.save(update_fields=["nums_watched"])

                    context = {
                        "is_right_student": is_right_student,
                        "is_activated": is_activated,
                        "message": message,
                        "lecture_id": video.lecture.id,
                        "enrollment_id": enrollment.id,
                        "player_embed_url": player_embed_url(uri),
                        "visit_times": enrollment.nums_watched[key],
                        "limit_exceeded": False
                    }
        else:
            context = {
                "is_right_student": is_right_student,
                "is_activated": is_activated,
                "message": message,
                "lecture_id": video.lecture.id,
                "enrollment_id": enrollment.id,
            }
    return render(request, template, context)


# test MAX_WATCH value
# from django.http import HttpResponse
# def test_max_watch(request):
#     return HttpResponse("Max watch number is %d" % MAX_WATCH)