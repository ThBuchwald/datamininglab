from django.views.generic import TemplateView
from django.urls import path
from main.views import say_hello, CreateHome, ExperimentCreateView, SampleCreateView, StaffCreateView, UserCreateView

urlpatterns = [
    path("hello/", say_hello),
    path("", TemplateView.as_view(template_name="main/index.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="main/about.html"), name="about"),
    path("impressum/", TemplateView.as_view(template_name="main/impressum.html"),
         name="impressum"),
    path("contact/", TemplateView.as_view(template_name="main/contact.html"), name="contact"),
    path("create/", CreateHome.as_view(), name="create"),
    path("create/sample", SampleCreateView.as_view(), name="sample_create"),
    path("create/experiment", ExperimentCreateView.as_view(),
         name="experiment_create"),
    path("create/staff", StaffCreateView.as_view(), name="staff_create"),
    path("create/user", UserCreateView.as_view(), name="user_create"),
]
