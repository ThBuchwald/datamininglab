from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from main.models import Experiment, FundingBody, Institute, Method, Project, Staff, Sample
from main.forms import ExperimentForm, FundingBodyForm, MethodForm, ProjectForm, SampleForm, StaffForm, UserForm, UserUpdateForm

''' ----------
    home views
    ---------- '''


class CreateHome(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url = reverse_lazy("login")
    template_name = "main/create.html"
    permission_required = "main.add_sample"


class UseHome(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url = reverse_lazy("login")
    template_name = "main/use.html"
    permission_required = "main.view_sample"


''' -------------
    CRUD - create
    ------------- '''


class ExperimentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
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
        form.instance.user = self.request.user
        return super(ExperimentCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('experiment_detail', kwargs={'pk': self.object.pk})


class ExperimentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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


class ExperimentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Experiment
    template_name = 'main/crud/experiment_detail.html'
    permission_required = "main.view_experiment"
    context_object_name = 'experiment'


class ExperimentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Experiment
    form_class = ExperimentForm
    template_name = 'main/crud/experiment_update.html'
    context_object_name = 'experiment'
    permission_required = "main.change_experiment"

    def get_queryset(self):
        return Experiment.objects.filter(institute__in=self.request.user.institute.all())

    def get_success_url(self):
        return reverse_lazy('experiment_detail', kwargs={'pk': self.object.pk})


class ExperimentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Experiment
    template_name = 'main/crud/experiment_delete.html'
    permission_required = "main.experiment_method"
    success_url = reverse_lazy("experiment_list")

    def get_queryset(self):
        return Experiment.objects.filter(institute__in=self.request.user.institute.all())


class FundingBodyCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = FundingBody
    form_class = FundingBodyForm
    template_name = 'main/crud/fundingbody_create.html'
    permission_required = "main.add_fundingbody"

    def get_success_url(self):
        return reverse_lazy('fundingbody_detail', kwargs={'pk': self.object.pk})


class FundingBodyListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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


class FundingBodyDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = FundingBody
    template_name = 'main/crud/fundingbody_detail.html'
    permission_required = "main.view_fundingbody"
    context_object_name = 'fundingbody'


class FundingBodyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = FundingBody
    form_class = FundingBodyForm
    template_name = 'main/crud/fundingbody_update.html'
    context_object_name = 'fundingbody'
    permission_required = "main.change_fundingbody"

    def get_success_url(self):
        return reverse_lazy('fundingbody_detail', kwargs={'pk': self.object.pk})


class FundingBodyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = FundingBody
    template_name = 'main/crud/fundingbody_delete.html'
    permission_required = "main.delete_fundingbody"
    success_url = reverse_lazy("fundingbody_list")


class InstituteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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


class InstituteDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Institute
    template_name = 'main/crud/institute_detail.html'
    permission_required = "main.view_institute"
    context_object_name = 'institute'


class MethodCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
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


class MethodListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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


class MethodDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Method
    template_name = 'main/crud/method_detail.html'
    permission_required = "main.view_method"
    context_object_name = 'method'


class MethodUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Method
    form_class = MethodForm
    template_name = 'main/crud/method_update.html'
    context_object_name = 'method'
    permission_required = "main.change_method"

    def get_queryset(self):
        return Method.objects.filter(institute__in=self.request.user.institute.all())

    def get_success_url(self):
        return reverse_lazy('method_detail', kwargs={'pk': self.object.pk})


class MethodDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Method
    template_name = 'main/crud/method_delete.html'
    permission_required = "main.delete_method"
    success_url = reverse_lazy("method_list")

    def get_queryset(self):
        return Method.objects.filter(institute__in=self.request.user.institute.all())


class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'main/crud/project_create.html'
    permission_required = "main.add_project"

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})


class ProjectListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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


class ProjectDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Project
    template_name = 'main/crud/project_detail.html'
    permission_required = "main.view_project"
    context_object_name = 'project'


class ProjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'main/crud/project_update.html'
    context_object_name = 'project'
    permission_required = "main.update_project"

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Project
    template_name = 'main/crud/project_delete.html'
    success_url = reverse_lazy("project_list")
    permission_required = "main.delete_project"


class SampleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
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
        return form

    def form_valid(self, form):
        # Set the 'user' field to the current user before saving the form
        form.instance.user = self.request.user
        return super(ExperimentCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('sample_detail', kwargs={'pk': self.object.pk})


class SampleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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


class SampleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Sample
    template_name = 'main/crud/sample_detail.html'
    permission_required = "main.view_sample"
    context_object_name = 'sample'


class SampleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Sample
    form_class = SampleForm
    template_name = 'main/crud/sample_update.html'
    context_object_name = 'sample'
    permission_required = "main.update_sample"

    def get_success_url(self):
        return reverse_lazy('sample_detail', kwargs={'pk': self.object.pk})


class SampleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Sample
    template_name = 'main/crud/sample_delete.html'
    success_url = reverse_lazy("sample_list")
    permission_required = "main.delete_sample"


class StaffCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
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


class StaffListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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


class StaffDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Staff
    template_name = 'main/crud/staff_detail.html'
    permission_required = "main.view_staff"
    context_object_name = 'staff'


class StaffUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'main/crud/staff_update.html'
    context_object_name = 'staff'
    permission_required = "main.update_staff"

    def get_queryset(self):
        return Staff.objects.filter(institute__in=self.request.user.institute.all())

    def get_success_url(self):
        return reverse_lazy('staff_detail', kwargs={'pk': self.object.pk})


class StaffDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Staff
    template_name = 'main/crud/staff_delete.html'
    success_url = reverse_lazy("staff_list")
    permission_required = "main.delete_staff"


User = get_user_model()


class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'main/crud/user_create.html'
    permission_required = "main.add_user"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.object.pk})


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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


class UserDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
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


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
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


class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
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
    # result = os.path.abspath(__file__)
    result = request.user.groups.all()[1:]
    return HttpResponse(result)
