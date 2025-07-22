from django.shortcuts import render, redirect

from django.views.generic import TemplateView, CreateView

from .forms import SignUpForm

from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy

from collections import defaultdict

class HomeView(TemplateView):
    template_name = 'common/home.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'common/dashboard.html'
    login_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get counts for the current user
        user_companies = Company.objects.filter(owner=self.request.user)
        context['companies_count'] = user_companies.count()
        
        # You can add more dashboard data here
        context['recent_companies'] = user_companies[:5]  # Latest 5 companies
        
        user_projects = Project.objects.filter(owner=self.request.user)
        context['active_projects_count'] = user_projects.count()
        context['recent_projects'] = user_projects[:5]  # Optional, if you want to show them

        # Contacts (placeholder)
        user_contacts = Contact.objects.filter(owner=self.request.user)
        context['contacts_count'] = user_contacts.count()
        context['recent_contacts'] = user_contacts[:5]
        # context['contacts_count'] = Contact.objects.filter(owner=self.request.user).count()

        user_earnings = EarningsModel.objects.filter(owner=self.request.user)

        # Update the existing earnings calculation to use real data:
        current_year = datetime.now().year
        current_month = datetime.now().month
        context['current_monthly_earnings'] = user_earnings.filter(
            year=current_year, 
            month=current_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Update chart data for dashboard
        context['earnings_chart_data'] = self.get_earnings_chart_data(user_earnings)
        context['sources_chart_data'] = self.get_sources_chart_data(user_earnings)

        return context
    
    def get_earnings_chart_data(self, earnings):
        current_year = datetime.now().year
        monthly_data = {}

        for earning in earnings.filter(year=current_year):
            month_name = earning.get_month_display()
            monthly_data[month_name] = monthly_data.get(month_name, 0) + float(earning.amount)

        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']

        return json.dumps({
            'labels': months,
            'data': [monthly_data.get(month, 0) for month in months]
        })

    def get_sources_chart_data(self, earnings):
        sources_data = earnings.values('source').annotate(total=Sum('amount')).order_by('-total')

        labels = []
        data = []
        for item in sources_data:
            source_display = dict(EarningsModel.SOURCE_CHOICES).get(item['source'], 'Other')
            labels.append(source_display)
            data.append(float(item['total']))

        return json.dumps({
            'labels': labels,
            'data': data
        })

class SignupView(CreateView):
    form_class = SignUpForm
    template_name = 'common/register.html'
    success_url =  reverse_lazy('home')
    
class CompanyView(LoginRequiredMixin, TemplateView):
    template_name = 'common/companies.html'

class ProjectsView(LoginRequiredMixin, TemplateView):
    template_name = 'common/projects.html'

class ContactView(LoginRequiredMixin, TemplateView):
    template_name = 'common/contacts.html'

    

from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import UserForm, ProfileForm
from django.contrib.auth.models import User
from apps.userprofile.models import Profile

from django.contrib import messages

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'common/profile.html'

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    user_form = UserForm
    profile_form = ProfileForm
    template_name = 'common/profile-update.html'

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        profile_form = ProfileForm(post_data, file_data, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.error(request, 'Your profile is updated successfully!')
            return HttpResponseRedirect(reverse_lazy('profile'))

        context = self.get_context_data(
                                        user_form=user_form,
                                        profile_form=profile_form
                                    )

        return self.render_to_response(context)     

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

from .models import Project
from .models import Company
from .models import Contact
from .forms import CompanyForm
from .forms import ContactForm

class CompanyView(LoginRequiredMixin, TemplateView):
    template_name = 'common/companies.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_form'] = CompanyForm()
        context['companies'] = Company.objects.filter(owner=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()
            messages.success(request, 'Company created successfully!')
            return redirect('companies')
        else:
            messages.error(request, 'Please correct the errors below.')
            
        context = self.get_context_data()
        context['company_form'] = form
        return self.render_to_response(context)
    
class ContactView(LoginRequiredMixin, TemplateView):
    template_name = 'common/contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_form'] = ContactForm()
        context['contacts'] = Contact.objects.filter(owner=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()
            messages.success(request, 'Contact created successfully!')
            return redirect('contacts')
        else:
            messages.error(request, 'Please correct the errors below.')
            
        context = self.get_context_data()
        context['contact_form'] = form
        return self.render_to_response(context)

from django.utils import timezone
from .forms import ProjectForm 

class ProjectsView(LoginRequiredMixin, TemplateView):
    template_name = 'common/projects.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_form'] = ProjectForm()
        context['projects'] = Project.objects.filter(owner=self.request.user)
        # Add statistics
        projects = context['projects']
        context['active_projects_count'] = projects.filter(status='active').count()
        context['completed_projects_count'] = projects.filter(status='completed').count()
        context['on_hold_projects_count'] = projects.filter(status='on_hold').count()
        context['overdue_projects_count'] = projects.filter(due_date__lt=timezone.now().date()).exclude(status='completed').count()
        return context
    
    def post(self, request, *args, **kwargs):
        project_form = ProjectForm(request.POST, user=request.user)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('projects')  # Make sure this URL name matches your urls.py
        
        # If form is invalid, return with errors
        context = self.get_context_data(**kwargs)
        context['project_form'] = project_form
        return self.render_to_response(context)
    
from .models import EarningsModel
from .forms import EarningsForm
from django.db.models import Sum
from datetime import datetime
import json

class EarningsView(LoginRequiredMixin, TemplateView):
    template_name = 'common/earnings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_earnings = EarningsModel.objects.filter(owner=self.request.user)
        
        # Basic stats
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        context['earning_form'] = EarningsForm()
        context['earnings'] = user_earnings
        context['total_year_earnings'] = user_earnings.filter(year=current_year).aggregate(Sum('amount'))['amount__sum'] or 0
        context['current_month_earnings'] = user_earnings.filter(year=current_year, month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0
        context['last_month_earnings'] = user_earnings.filter(
            year=current_year if current_month > 1 else current_year-1, 
            month=current_month-1 if current_month > 1 else 12
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        context['active_sources_count'] = user_earnings.values('source').distinct().count()
        
        # Chart data for dashboard integration
        context['earnings_chart_data'] = self.get_earnings_chart_data(user_earnings)
        context['sources_chart_data'] = self.get_sources_chart_data(user_earnings)
        
        return context
    
    def post(self, request, *args, **kwargs):
        earning_form = EarningsForm(request.POST)
        if earning_form.is_valid():
            earning = earning_form.save(commit=False)
            earning.owner = request.user
            earning.save()
            messages.success(request, 'Monthly earning added successfully!')
            return redirect('earnings')
        
        context = self.get_context_data(**kwargs)
        context['earning_form'] = earning_form
        return self.render_to_response(context)
    
    def get_earnings_chart_data(self, earnings):
        # Generate monthly data for the current year
        current_year = datetime.now().year
        monthly_data = {}
        
        for earning in earnings.filter(year=current_year):
            month_name = earning.get_month_display()
            if month_name in monthly_data:
                monthly_data[month_name] += float(earning.amount)
            else:
                monthly_data[month_name] = float(earning.amount)
        
        # Ensure all months are represented
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        return json.dumps({
            'labels': months,
            'data': [monthly_data.get(month, 0) for month in months]
        })
    
    def get_sources_chart_data(self, earnings):
        sources_data = earnings.values('source').annotate(total=Sum('amount')).order_by('-total')
        
        labels = []
        data = []
        for item in sources_data:
            source_display = dict(EarningsModel.SOURCE_CHOICES)[item['source']]
            labels.append(source_display)
            data.append(float(item['total']))
        
        return json.dumps({
            'labels': labels,
            'data': data
        })