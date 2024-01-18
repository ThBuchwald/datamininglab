from django.views.generic import TemplateView
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .views import (CreateHome, UseHome,
                    ExperimentCreateView, ExperimentListView, ExperimentDetailView, ExperimentUpdateView, ExperimentDeleteView,
                    FundingBodyCreateView, FundingBodyListView, FundingBodyDetailView, FundingBodyUpdateView, FundingBodyDeleteView,
                    InstituteListView, InstituteDetailView,
                    MethodCreateView, MethodListView, MethodDetailView, MethodUpdateView, MethodDeleteView,
                    ProjectCreateView, ProjectListView, ProjectDetailView, ProjectUpdateView, ProjectDeleteView,
                    SampleCreateView, SampleListView, SampleDetailView, SampleUpdateView, SampleDeleteView,
                    StaffCreateView, StaffListView, StaffDetailView, StaffUpdateView, StaffDeleteView,
                    UserCreateView, UserListView, UserDetailView, UserUpdateView, UserDeleteView,
                    SampleViewSet, ExperimentViewSet, FundingBodyViewSet, InstituteViewSet, MethodViewSet, ProjectViewSet, SampleTypeViewSet, StaffViewSet,
                    ChooseSampleInfoView, CreateSampleInfoView, sample_type_info, say_hello)

router = DefaultRouter()
router.register(r'samples', SampleViewSet)
router.register(r'experiments', ExperimentViewSet)
router.register(r'fundingbodies', FundingBodyViewSet)
router.register(r'institutes', InstituteViewSet)
router.register(r'methods', MethodViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'sampletypes', SampleTypeViewSet)
router.register(r'staff', StaffViewSet)

urlpatterns = [
    path("hello/", say_hello),

    path("", TemplateView.as_view(template_name="main/index.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="main/about.html"), name="about"),
    path("contact/", TemplateView.as_view(template_name="main/contact.html"), name="contact"),
    path("impressum/", TemplateView.as_view(template_name="main/impressum.html"),
         name="impressum"),

    path("create/", CreateHome.as_view(), name="create"),
    path("use/", UseHome.as_view(), name="use"),

    path("experiment/create", ExperimentCreateView.as_view(),
         name="experiment_create"),
    path('experiment/', ExperimentListView.as_view(), name='experiment_list'),
    path('experiment/<int:pk>/', ExperimentDetailView.as_view(),
         name='experiment_detail'),
    path('experiment/<int:pk>/update/',
         ExperimentUpdateView.as_view(), name='experiment_update'),
    path('experiment/<int:pk>/delete/',
         ExperimentDeleteView.as_view(), name='experiment_delete'),

    path("fundingbody/create", FundingBodyCreateView.as_view(),
         name="fundingbody_create"),
    path('fundingbody/', FundingBodyListView.as_view(), name='fundingbody_list'),
    path('fundingbody/<int:pk>/', FundingBodyDetailView.as_view(),
         name='fundingbody_detail'),
    path('fundingbody/<int:pk>/update/',
         FundingBodyUpdateView.as_view(), name='fundingbody_update'),
    path('fundingbody/<int:pk>/delete/',
         FundingBodyDeleteView.as_view(), name='fundingbody_delete'),

    path('institute/', InstituteListView.as_view(), name='institute_list'),
    path('institute/<int:pk>/', InstituteDetailView.as_view(),
         name='institute_detail'),

    path("method/create", MethodCreateView.as_view(), name="method_create"),
    path('method/', MethodListView.as_view(), name='method_list'),
    path('method/<int:pk>/', MethodDetailView.as_view(), name='method_detail'),
    path('method/<int:pk>/update/',
         MethodUpdateView.as_view(), name='method_update'),
    path('method/<int:pk>/delete/',
         MethodDeleteView.as_view(), name='method_delete'),

    path("project/create", ProjectCreateView.as_view(), name="project_create"),
    path('project/', ProjectListView.as_view(), name='project_list'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/update/',
         ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/',
         ProjectDeleteView.as_view(), name='project_delete'),

    path("sample_info/choose", ChooseSampleInfoView.as_view(), name="sample_info_choose"),
    path("sample_info/create", CreateSampleInfoView.as_view(), name="sample_info_create"),

    path("sample/create", SampleCreateView.as_view(), name="sample_create"),
    path('sample/', SampleListView.as_view(), name='sample_list'),
    # the sample URLs all contain underscores because of their special pk
    # therefore "int:" needed to be removed to properly display entries
    path('sample/<pk>/', SampleDetailView.as_view(), name='sample_detail'),
    path('sample/<pk>/update/',
         SampleUpdateView.as_view(), name='sample_update'),
    path('sample/<pk>/delete/',
         SampleDeleteView.as_view(), name='sample_delete'),

    path("staff/create", StaffCreateView.as_view(), name="staff_create"),
    path('staff/', StaffListView.as_view(), name='staff_list'),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff_detail'),
    path('staff/<int:pk>/update/', StaffUpdateView.as_view(), name='staff_update'),
    path('staff/<int:pk>/delete/', StaffDeleteView.as_view(), name='staff_delete'),

    path("user/create", UserCreateView.as_view(), name="user_create"),
    path('user/', UserListView.as_view(), name='user_list'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('user/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
]

# API-related

urlpatterns += [path('api-token-auth/', obtain_auth_token,
                     name='api-token-auth'),
                path('api/sample-type-info/<str:sample_type_name>/', 
                     sample_type_info, name='sample_type_info'),
               ]

urlpatterns += router.urls
