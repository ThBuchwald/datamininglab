import json
import logging
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Experiment, FundingBody, Institute, Method, Project, Staff, Sample, SampleType
from .forms import ExperimentForm, FundingBodyForm, MethodForm, ProjectForm, SampleForm, SampleInfoForm, StaffForm, UserForm, UserUpdateForm
from .serializers.sample_type_serializers import (
    SampleTypeBatterySerializer, SampleTypeSolidsSerializer, SampleTypeLiquidSerializer, SampleTypeSuspensionSerializer
)

logger = logging.getLogger(__name__) # main.views


# This class supersedes LoginRequiredMixin and PermissionRequiredMixin and adds logging for all (non-API) Views
class LoggingPermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Mixin that logs unauthorized access attempts and enforces permission checks.
    """
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            logger.warning(
                f"Unauthorized access attempt to {self.request.path} by an unauthenticated user (IP: {self.request.META.get('REMOTE_ADDR')})."
            )
        else:
            logger.warning(
                f"Unauthorized access attempt to {self.request.path} by user {self.request.user.username} "
                f"(Required Permissions: {self.permission_required})."
            )
        return super().handle_no_permission()


''' ----------
    home views
    ---------- '''


class CreateHome(LoggingPermissionRequiredMixin, TemplateView):
    login_url = reverse_lazy("login")
    template_name = "main/create.html"
    permission_required = "main.add_sample"


class UseHome(LoggingPermissionRequiredMixin, TemplateView):
    login_url = reverse_lazy("login")
    template_name = "main/use.html"
    permission_required = "main.view_sample"


''' ----------------
    Sample Info File
    ---------------- '''


class ChooseSampleInfoView(LoggingPermissionRequiredMixin, View):
    permission_required = "main.add_sample"
    
    def get(self, request):
        # Retrieve all SampleType objects from the database
        sample_types = SampleType.objects.all()
        # Render the template with the list of sample types
        return render(request, 'main/crud/sample_info_choose.html', {'sample_types': sample_types})


class CreateSampleInfoView(LoggingPermissionRequiredMixin, FormView):
    permission_required = "main.add_sample"
    template_name = 'main/crud/sample_info_create.html'
    form_class = SampleInfoForm

    def get_form_kwargs(self):
        kwargs = super(CreateSampleInfoView, self).get_form_kwargs()
        sample_type_id = self.request.GET.get('sample_type')
        sample_type_name = SampleType.objects.get(pk=sample_type_id).name
        
        # Map sample type names to serializer classes as before
        sample_type_serializers = {
            'Battery': SampleTypeBatterySerializer,
            'Solids': SampleTypeSolidsSerializer,
            'Liquid': SampleTypeLiquidSerializer,
            'Suspension': SampleTypeSuspensionSerializer,
        }
        
        # Pass the serializer class for the chosen sample type to the form
        kwargs['serializer_class'] = sample_type_serializers.get(sample_type_name.capitalize())
        return kwargs

    def form_valid(self, form):
        # Convert the cleaned data dict to JSON using Django's encoder
        sample_info_json = json.dumps(form.cleaned_data, cls=DjangoJSONEncoder)
        
        # Construct the HTTP response
        response = HttpResponse(sample_info_json, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="sample_info.json"'
        return response


''' -----------------
    CRUD - Experiment
    ----------------- '''


class ExperimentCreateView(LoggingPermissionRequiredMixin, CreateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = 'main/crud/experiment_create.html'
    permission_required = "main.add_experiment"

    def get_form(self, *args, **kwargs):
        form = super(ExperimentCreateView, self).get_form(*args, **kwargs)
        # Get the institutes that the current user belongs to
        user_institutes = self.request.user.institute.all()
        # Modify the queryset for the 'staff' field to only include staff that belongs to the user's institutes
        form.fields['staff'].queryset = Staff.objects.filter(
            institute__in=user_institutes)
        form.fields['method'].queryset = Method.objects.filter(
            institute__in=user_institutes)
        return form

    def form_valid(self, form):
        # Set the 'user' field to the current user before saving the form
        print(form.errors)
        form.instance.user = self.request.user
        return super(ExperimentCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('experiment_detail', kwargs={'pk': self.object.pk})


class ExperimentListView(LoggingPermissionRequiredMixin, ListView):
    model = Experiment
    template_name = "main/crud/experiment_list.html"
    permission_required = "main.view_experiment"
    context_object_name = "experiments"

    def get_queryset(self):
        queryset = Experiment.objects.select_related('sample').all()

        sort_by = self.request.GET.get('sort_by', '')

        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')
        elif sort_by == 'sample':
            queryset = queryset.order_by('sample__sample_id')
        elif sort_by == 'sample_desc':
            queryset = queryset.order_by('-sample__sample_id')
        elif sort_by == 'date':
            queryset = queryset.order_by('date_registered')
        elif sort_by == 'date_desc':
            queryset = queryset.order_by('-date_registered')

        return queryset


class ExperimentDetailView(LoggingPermissionRequiredMixin, DetailView):
    model = Experiment
    template_name = 'main/crud/experiment_detail.html'
    permission_required = "main.view_experiment"
    context_object_name = 'experiment'


class ExperimentUpdateView(LoggingPermissionRequiredMixin, UpdateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = 'main/crud/experiment_update.html'
    context_object_name = 'experiment'
    permission_required = "main.change_experiment"

    def get_form(self, *args, **kwargs):
        form = super(ExperimentUpdateView, self).get_form(*args, **kwargs)
        # Get the institutes that the current user belongs to
        user_institutes = self.request.user.institute.all()
        # Modify the queryset for the 'staff' field to only include staff that belongs to the user's institutes
        form.fields['staff'].queryset = Staff.objects.filter(
            institute__in=user_institutes)
        form.fields['method'].queryset = Method.objects.filter(
            institute__in=user_institutes)
        return form

    def form_valid(self, form):
        # Set the 'user' field to the current user before saving the form
        print(form.errors)
        form.instance.user = self.request.user
        return super(ExperimentUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('experiment_detail', kwargs={'pk': self.object.pk})


class ExperimentDeleteView(LoggingPermissionRequiredMixin, DeleteView):
    model = Experiment
    template_name = 'main/crud/experiment_delete.html'
    permission_required = "main.experiment_method"
    success_url = reverse_lazy("experiment_list")


''' ------------------
    CRUD - FundingBody
    ------------------ '''


class FundingBodyCreateView(LoggingPermissionRequiredMixin, CreateView):
    model = FundingBody
    form_class = FundingBodyForm
    template_name = 'main/crud/fundingbody_create.html'
    permission_required = "main.add_fundingbody"

    def get_success_url(self):
        return reverse_lazy('fundingbody_detail', kwargs={'pk': self.object.pk})


class FundingBodyListView(LoggingPermissionRequiredMixin, ListView):
    model = FundingBody
    template_name = 'main/crud/fundingbody_list.html'
    permission_required = "main.view_fundingbody"
    context_object_name = 'fundingbodies'

    def get_queryset(self):
        queryset = FundingBody.objects.all()

        sort_by = self.request.GET.get('sort_by', '')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')

        return queryset


class FundingBodyDetailView(LoggingPermissionRequiredMixin, DetailView):
    model = FundingBody
    template_name = 'main/crud/fundingbody_detail.html'
    permission_required = "main.view_fundingbody"
    context_object_name = 'fundingbody'


class FundingBodyUpdateView(LoggingPermissionRequiredMixin, UpdateView):
    model = FundingBody
    form_class = FundingBodyForm
    template_name = 'main/crud/fundingbody_update.html'
    context_object_name = 'fundingbody'
    permission_required = "main.change_fundingbody"

    def get_success_url(self):
        return reverse_lazy('fundingbody_detail', kwargs={'pk': self.object.pk})


class FundingBodyDeleteView(LoggingPermissionRequiredMixin, DeleteView):
    model = FundingBody
    template_name = 'main/crud/fundingbody_delete.html'
    permission_required = "main.delete_fundingbody"
    success_url = reverse_lazy("fundingbody_list")


''' ----------------
    CRUD - Institute
    ---------------- '''


class InstituteListView(LoggingPermissionRequiredMixin, ListView):
    model = Institute
    template_name = 'main/crud/institute_list.html'
    permission_required = "main.view_institute"
    context_object_name = 'institutes'

    def get_queryset(self):
        queryset = Institute.objects.all()

        sort_by = self.request.GET.get('sort_by', '')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')

        return queryset


class InstituteDetailView(LoggingPermissionRequiredMixin, DetailView):
    model = Institute
    template_name = 'main/crud/institute_detail.html'
    permission_required = "main.view_institute"
    context_object_name = 'institute'


''' -------------
    CRUD - Method
    ------------- '''


class MethodCreateView(LoggingPermissionRequiredMixin, CreateView):
    model = Method
    form_class = MethodForm
    template_name = 'main/crud/method_create.html'
    permission_required = "main.add_method"

    def get_form(self, *args, **kwargs):
        form = super(MethodCreateView, self).get_form(*args, **kwargs)
        form.fields['institute'].queryset = self.request.user.institute.all()
        # the AdminGroup is exluded in this list to prevent admins from creating new admins
        return form

    def get_success_url(self):
        return reverse_lazy('method_detail', kwargs={'pk': self.object.pk})


class MethodListView(LoggingPermissionRequiredMixin, ListView):
    model = Method
    template_name = 'main/crud/method_list.html'
    permission_required = "main.view_method"
    context_object_name = 'methods'

    def get_queryset(self):
        queryset = Method.objects.filter(
            institute__in=self.request.user.institute.all())

        only_institute = self.request.GET.get('institute', '')
        if self.request.user.institute != None and only_institute == "true":
            queryset = queryset.filter(
                institute__in=self.request.user.institute.all())
        else:
            queryset = queryset

        sort_by = self.request.GET.get('sort_by', '')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')
        elif sort_by == 'date':
            queryset = queryset.order_by('date_registered')
        elif sort_by == 'date_desc':
            queryset = queryset.order_by('-date_registered')

        return queryset


class MethodDetailView(LoggingPermissionRequiredMixin, DetailView):
    model = Method
    template_name = 'main/crud/method_detail.html'
    permission_required = "main.view_method"
    context_object_name = 'method'


class MethodUpdateView(LoggingPermissionRequiredMixin, UpdateView):
    model = Method
    form_class = MethodForm
    template_name = 'main/crud/method_update.html'
    context_object_name = 'method'
    permission_required = "main.change_method"

    def get_queryset(self):
        return Method.objects.filter(institute__in=self.request.user.institute.all())

    def get_success_url(self):
        return reverse_lazy('method_detail', kwargs={'pk': self.object.pk})


class MethodDeleteView(LoggingPermissionRequiredMixin, DeleteView):
    model = Method
    template_name = 'main/crud/method_delete.html'
    permission_required = "main.delete_method"
    success_url = reverse_lazy("method_list")

    def get_queryset(self):
        return Method.objects.filter(institute__in=self.request.user.institute.all())


''' --------------
    CRUD - Project
    -------------- '''


class ProjectCreateView(LoggingPermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'main/crud/project_create.html'
    permission_required = "main.add_project"

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})


class ProjectListView(LoggingPermissionRequiredMixin, ListView):
    model = Project
    template_name = 'main/crud/project_list.html'
    permission_required = "main.view_project"
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = Project.objects.all()

        sort_by = self.request.GET.get('sort_by', '')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')
        elif sort_by == 'number':
            queryset = queryset.order_by('funding_number')
        elif sort_by == 'number_desc':
            queryset = queryset.order_by('-funding_number')

        return queryset


class ProjectDetailView(LoggingPermissionRequiredMixin, DetailView):
    model = Project
    template_name = 'main/crud/project_detail.html'
    permission_required = "main.view_project"
    context_object_name = 'project'


class ProjectUpdateView(LoggingPermissionRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'main/crud/project_update.html'
    context_object_name = 'project'
    permission_required = "main.update_project"

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoggingPermissionRequiredMixin, DeleteView):
    model = Project
    template_name = 'main/crud/project_delete.html'
    success_url = reverse_lazy("project_list")
    permission_required = "main.delete_project"


''' -------------
    CRUD - Sample
    ------------- '''


class SampleCreateView(LoggingPermissionRequiredMixin, CreateView):
    model = Sample
    form_class = SampleForm
    template_name = 'main/crud/sample_create.html'
    permission_required = "main.add_sample"

    # get_form is superseded to only send institutes belonging to the current user
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    def get_form(self, *args, **kwargs):
        form = super(SampleCreateView, self).get_form(*args, **kwargs)
        user_institutes = self.request.user.institute.all()
        form.fields['institute'].queryset = user_institutes
        form.fields['method'].queryset = Method.objects.filter(
            institute__in=user_institutes)
        form.fields['parent'].queryset = Sample.objects.filter(
            institute__in=user_institutes)
        #form.fields['sample_type'].queryset = SampleType.objects.all()
        return form

    def form_valid(self, form):
        # Check if form inputs are valid
        if form.is_valid():
            # Set the 'user' field to the current user before saving the form
            form.instance.user = self.request.user
            # Here, we print the user to the console
            print("User: ", self.request.user)
            # Call the parent form_valid method which also saves the form
            return super(SampleCreateView, self).form_valid(form)

    def form_invalid(self, form):
        # Log form errors to console
        print("Form is not valid :(")
        print(form.errors)
        # Call parent function
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('sample_detail', kwargs={'pk': self.object.pk})


class SampleListView(LoggingPermissionRequiredMixin, ListView):
    model = Sample
    template_name = 'main/crud/sample_list.html'
    permission_required = "main.view_sample"
    context_object_name = 'samples'

    def get_queryset(self):
        queryset = Sample.objects.all()

        only_institute = self.request.GET.get('institute', '')
        if self.request.user.institute != None and only_institute == "true":
            queryset = queryset.filter(
                institute__in=self.request.user.institute.all())
        else:
            queryset = queryset

        sort_by = self.request.GET.get('sort_by', '')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')
        elif sort_by == 'sample_id':
            queryset = queryset.order_by('sample_id')
        elif sort_by == 'sample_id_desc':
            queryset = queryset.order_by('-sample_id')
        elif sort_by == 'date':
            queryset = queryset.order_by('date_registered')
        elif sort_by == 'date_desc':
            queryset = queryset.order_by('-date_registered')

        return queryset


class SampleDetailView(LoggingPermissionRequiredMixin, DetailView):
    model = Sample
    template_name = 'main/crud/sample_detail.html'
    permission_required = "main.view_sample"
    context_object_name = 'sample'


class SampleUpdateView(LoggingPermissionRequiredMixin, UpdateView):
    model = Sample
    form_class = SampleForm
    template_name = 'main/crud/sample_update.html'
    context_object_name = 'sample'
    permission_required = "main.update_sample"

    def get_form(self, *args, **kwargs):
        form = super(SampleUpdateView, self).get_form(*args, **kwargs)
        user_institutes = self.request.user.institute.all()
        form.fields['institute'].queryset = user_institutes
        form.fields['method'].queryset = Method.objects.filter(
            institute__in=user_institutes)
        form.fields['parent'].queryset = Sample.objects.filter(
            institute__in=user_institutes)
        #form.fields['sample_type'].queryset = SampleType.objects.all()
        return form

    def form_valid(self, form):
        # Check if form inputs are valid
        if form.is_valid():
            # Set the 'user' field to the current user before saving the form
            form.instance.user = self.request.user
            # Here, we print the user to the console
            print("User: ", self.request.user)
            # Call the parent form_valid method which also saves the form
            return super(SampleUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        # Log form errors to console
        print("Form is not valid :(")
        print(form.errors)
        # Call parent function
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('sample_detail', kwargs={'pk': self.object.pk})


class SampleDeleteView(LoggingPermissionRequiredMixin, DeleteView):
    model = Sample
    template_name = 'main/crud/sample_delete.html'
    success_url = reverse_lazy("sample_list")
    permission_required = "main.delete_sample"


''' ------------
    CRUD - Staff
    ------------ '''


class StaffCreateView(LoggingPermissionRequiredMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'main/crud/staff_create.html'
    permission_required = "main.add_staff"

    def get_form(self, *args, **kwargs):
        form = super(StaffCreateView, self).get_form(*args, **kwargs)
        form.fields['institute'].queryset = self.request.user.institute.all()
        # the AdminGroup is exluded in this list to prevent admins from creating new admins
        return form

    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.pk})


class StaffListView(LoggingPermissionRequiredMixin, ListView):
    model = Staff
    template_name = 'main/crud/staff_list.html'
    permission_required = "main.view_staff"
    context_object_name = 'staff'

    def get_queryset(self):
        queryset = Staff.objects.all()

        only_institute = self.request.GET.get('institute', '')
        if self.request.user.institute != None and only_institute == "true":
            queryset = queryset.filter(
                institute__in=self.request.user.institute.all())
        else:
            queryset = queryset

        sort_by = self.request.GET.get('sort_by', '')
        if sort_by == 'first_name':
            queryset = queryset.order_by('first_name')
        elif sort_by == 'first_name_desc':
            queryset = queryset.order_by('-first_name')
        elif sort_by == 'last_name':
            queryset = queryset.order_by('last_name')
        elif sort_by == 'last_name_desc':
            queryset = queryset.order_by('-last_name')

        return queryset


class StaffDetailView(LoggingPermissionRequiredMixin, DetailView):
    model = Staff
    template_name = 'main/crud/staff_detail.html'
    permission_required = "main.view_staff"
    context_object_name = 'staff'


class StaffUpdateView(LoggingPermissionRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'main/crud/staff_update.html'
    context_object_name = 'staff'
    permission_required = "main.update_staff"

    def get_queryset(self):
        return Staff.objects.filter(institute__in=self.request.user.institute.all())

    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.pk})


class StaffDeleteView(LoggingPermissionRequiredMixin, DeleteView):
    model = Staff
    template_name = 'main/crud/staff_delete.html'
    success_url = reverse_lazy("staff_list")
    permission_required = "main.delete_staff"


''' -----------
    CRUD - User
    ----------- '''

User = get_user_model()


class UserCreateView(LoggingPermissionRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'main/crud/user_create.html'
    permission_required = "main.add_user"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.object.pk})


class UserListView(LoggingPermissionRequiredMixin, ListView):
    model = User
    template_name = 'main/crud/user_list.html'
    permission_required = "main.view_user"
    context_object_name = 'users'

    def get_queryset(self):
        queryset = User.objects.all()

        only_institute = self.request.GET.get('institute', '')
        if self.request.user.institute != None and only_institute == "true":
            queryset = queryset.filter(
                institute__in=self.request.user.institute.all())
        else:
            queryset = queryset

        sort_by = self.request.GET.get('sort_by', '')
        if sort_by == 'username':
            queryset = queryset.order_by('username')
        elif sort_by == 'username_desc':
            queryset = queryset.order_by('-username')
        elif sort_by == 'email':
            queryset = queryset.order_by('email')
        elif sort_by == 'email_desc':
            queryset = queryset.order_by('-email')

        return queryset


class UserDetailView(LoggingPermissionRequiredMixin, DetailView):
    model = User
    template_name = 'main/crud/user_detail.html'
    permission_required = "main.view_user"
    context_object_name = 'user'

    def get_queryset(self):
        return User.objects.filter(institute__in=self.request.user.institute.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = self.object.groups.all()
        context['institutes'] = self.object.institute.all()
        return context


class UserUpdateView(LoggingPermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'main/crud/user_update.html'
    context_object_name = 'user'
    permission_required = "main.update_user"

    def get_queryset(self):
        return User.objects.filter(institute__in=self.request.user.institute.all())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.object.pk})


class UserDeleteView(LoggingPermissionRequiredMixin, DeleteView):
    model = User
    template_name = 'main/crud/user_delete.html'
    success_url = reverse_lazy("user_list")
    permission_required = "main.delete_user"

    def get_queryset(self):
        return User.objects.filter(institute__in=self.request.user.institute.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = self.object.groups.all()
        context['institutes'] = self.object.institute.all()
        return context


''' ----------------
    playground views
    ---------------- '''


def say_hello(request):
    result = request.user.groups.all()[1:]
    return HttpResponse(result)
