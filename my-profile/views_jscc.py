"""Private JSCC (Job Search Command Center) views. Every record belongs to one user."""
import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import (
    ApplicationForm, ChecklistItemForm, NetworkContactForm, RoadmapItemForm, UserSettingsForm,
)
from .models import Application, ChecklistItem, NetworkContact, RoadmapItem, UserSettings

DEFAULT_CHECKLIST = [
    ('resume', 'Update resume with latest role and measurable results'),
    ('resume', 'Save a PDF version of the resume'),
    ('linkedin', 'Refresh LinkedIn headline and About section'),
    ('linkedin', 'Turn on "Open to work" for recruiters'),
    ('portfolio', 'Publish two case studies'),
    ('portfolio', 'Check every portfolio link and the contact form'),
    ('networking', 'Message five former colleagues'),
    ('networking', 'Ask one person for a referral'),
    ('interview', 'Prepare five STAR stories'),
    ('interview', 'Research the next interviewer on LinkedIn'),
    ('admin', 'Set weekly application and outreach goals'),
    ('admin', 'Keep a log of every application in JSCC'),
]


def start_of_week(today):
    return today - timedelta(days=today.weekday())


# --------------------------------------------------------------------------- mixins
class OwnedMixin(LoginRequiredMixin):
    """Restrict every query to the signed-in user's own records."""

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class OwnedFormMixin(OwnedMixin, SuccessMessageMixin):
    template_name = "jscc/form.html"
    page_title = ""
    cancel_url = None

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['cancel_url'] = self.cancel_url or self.success_url
        return context


class OwnedDeleteMixin(OwnedMixin):
    template_name = "jscc/confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.success_url
        return context

    def form_valid(self, form):
        messages.success(self.request, "Deleted.")
        return super().form_valid(form)


# --------------------------------------------------------------------------- dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "jscc/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()
        apps = Application.objects.filter(owner=user)
        total = apps.count()

        pipeline = []
        for value, label in Application.STATUS_CHOICES:
            count = apps.filter(status=value).count()
            pipeline.append({
                'value': value, 'label': label, 'count': count,
                'percent': round(count * 100 / total) if total else 0,
            })

        settings_obj, _ = UserSettings.objects.get_or_create(user=user)
        week_start = start_of_week(today)
        applied_this_week = apps.filter(applied_on__gte=week_start).count()
        goal = settings_obj.weekly_application_goal or 0
        checklist = ChecklistItem.objects.filter(owner=user)
        checklist_total = checklist.count()
        checklist_done = checklist.filter(is_done=True).count()

        context.update({
            'total': total,
            'active_count': apps.filter(status__in=Application.ACTIVE_STATUSES).count(),
            'interview_count': apps.filter(status=Application.INTERVIEW).count(),
            'offer_count': apps.filter(status=Application.OFFER).count(),
            'pipeline': pipeline,
            'applied_this_week': applied_this_week,
            'weekly_goal': goal,
            'weekly_percent': min(100, round(applied_this_week * 100 / goal)) if goal else 0,
            'upcoming': apps.filter(next_step_date__gte=today).exclude(
                status__in=[Application.REJECTED, Application.WITHDRAWN]).order_by('next_step_date')[:5],
            'follow_ups': NetworkContact.objects.filter(
                owner=user, follow_up_on__isnull=False,
                follow_up_on__lte=today + timedelta(days=7)).order_by('follow_up_on')[:5],
            'checklist_total': checklist_total,
            'checklist_done': checklist_done,
            'checklist_percent': round(checklist_done * 100 / checklist_total) if checklist_total else 0,
            'now_items': RoadmapItem.objects.filter(owner=user, phase=RoadmapItem.NOW).exclude(
                status=RoadmapItem.DONE)[:4],
            'today': today,
        })
        return context


# --------------------------------------------------------------------------- applications
class ApplicationListView(OwnedMixin, ListView):
    model = Application
    template_name = "jscc/applications.html"
    context_object_name = "applications"

    def get_queryset(self):
        qs = super().get_queryset()
        self.status = self.request.GET.get('status', '')
        self.query = self.request.GET.get('q', '').strip()
        if self.status in dict(Application.STATUS_CHOICES):
            qs = qs.filter(status=self.status)
        else:
            self.status = ''
        if self.query:
            qs = qs.filter(Q(company__icontains=self.query) | Q(role_title__icontains=self.query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view = self.request.GET.get('view', 'table')
        context['view'] = view if view in ('table', 'board') else 'table'
        context['status'] = self.status
        context['query'] = self.query
        context['status_choices'] = Application.STATUS_CHOICES
        apps = list(context['applications'])
        context['columns'] = [
            {'value': value, 'label': label, 'items': [a for a in apps if a.status == value]}
            for value, label in Application.STATUS_CHOICES
        ]
        return context


class ApplicationCreateView(OwnedFormMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    success_url = reverse_lazy('jscc-application-list')
    success_message = "Application added."
    page_title = "Add application"


class ApplicationUpdateView(OwnedFormMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    success_url = reverse_lazy('jscc-application-list')
    success_message = "Application updated."
    page_title = "Edit application"


class ApplicationDeleteView(OwnedDeleteMixin, DeleteView):
    model = Application
    success_url = reverse_lazy('jscc-application-list')


class ApplicationExportView(LoginRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="applications.csv"'
        writer = csv.writer(response)
        writer.writerow(['Company', 'Role', 'Status', 'Location', 'Applied on', 'Next step',
                         'Next step date', 'Source', 'Job URL', 'Notes'])
        for a in Application.objects.filter(owner=request.user):
            writer.writerow([a.company, a.role_title, a.get_status_display(), a.location,
                             a.applied_on or '', a.next_step, a.next_step_date or '',
                             a.source, a.job_url, a.notes])
        return response


# --------------------------------------------------------------------------- roadmap
class RoadmapListView(OwnedMixin, ListView):
    model = RoadmapItem
    template_name = "jscc/roadmap.html"
    context_object_name = "items"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = list(context['items'])
        context['phases'] = [
            {'value': value, 'label': label, 'items': [i for i in items if i.phase == value]}
            for value, label in RoadmapItem.PHASE_CHOICES
        ]
        return context


class RoadmapCreateView(OwnedFormMixin, CreateView):
    model = RoadmapItem
    form_class = RoadmapItemForm
    success_url = reverse_lazy('jscc-roadmap-list')
    success_message = "Roadmap item added."
    page_title = "Add roadmap item"


class RoadmapUpdateView(OwnedFormMixin, UpdateView):
    model = RoadmapItem
    form_class = RoadmapItemForm
    success_url = reverse_lazy('jscc-roadmap-list')
    success_message = "Roadmap item updated."
    page_title = "Edit roadmap item"


class RoadmapDeleteView(OwnedDeleteMixin, DeleteView):
    model = RoadmapItem
    success_url = reverse_lazy('jscc-roadmap-list')


# --------------------------------------------------------------------------- checklist
class ChecklistView(LoginRequiredMixin, TemplateView):
    template_name = "jscc/checklist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = list(ChecklistItem.objects.filter(owner=self.request.user))
        done = sum(1 for i in items if i.is_done)
        context.update({
            'groups': [
                {'value': value, 'label': label, 'items': [i for i in items if i.category == value]}
                for value, label in ChecklistItem.CATEGORY_CHOICES
                if any(i.category == value for i in items)
            ],
            'form': kwargs.get('form') or ChecklistItemForm(),
            'total': len(items),
            'done': done,
            'percent': round(done * 100 / len(items)) if items else 0,
        })
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('action') == 'seed':
            if not ChecklistItem.objects.filter(owner=request.user).exists():
                ChecklistItem.objects.bulk_create([
                    ChecklistItem(owner=request.user, category=cat, title=title, sort_order=i)
                    for i, (cat, title) in enumerate(DEFAULT_CHECKLIST)
                ])
                messages.success(request, "Starter checklist added.")
            return redirect('jscc-checklist')
        form = ChecklistItemForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            messages.success(request, "Task added.")
            return redirect('jscc-checklist')
        return self.render_to_response(self.get_context_data(form=form))


class ChecklistToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(ChecklistItem, pk=pk, owner=request.user)
        item.is_done = not item.is_done
        item.completed_at = timezone.now() if item.is_done else None
        item.save(update_fields=['is_done', 'completed_at'])
        return redirect('jscc-checklist')


class ChecklistDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        get_object_or_404(ChecklistItem, pk=pk, owner=request.user).delete()
        return redirect('jscc-checklist')


# --------------------------------------------------------------------------- contacts
class ContactListView(OwnedMixin, ListView):
    model = NetworkContact
    template_name = "jscc/contacts.html"
    context_object_name = "contacts"

    def get_queryset(self):
        qs = super().get_queryset()
        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            qs = qs.filter(Q(name__icontains=self.query) | Q(company__icontains=self.query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        context['today'] = timezone.localdate()
        return context


class ContactCreateView(OwnedFormMixin, CreateView):
    model = NetworkContact
    form_class = NetworkContactForm
    success_url = reverse_lazy('jscc-contact-list')
    success_message = "Contact added."
    page_title = "Add contact"


class ContactUpdateView(OwnedFormMixin, UpdateView):
    model = NetworkContact
    form_class = NetworkContactForm
    success_url = reverse_lazy('jscc-contact-list')
    success_message = "Contact updated."
    page_title = "Edit contact"


class ContactDeleteView(OwnedDeleteMixin, DeleteView):
    model = NetworkContact
    success_url = reverse_lazy('jscc-contact-list')


# --------------------------------------------------------------------------- settings
class SettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "jscc/settings.html"
    form_class = UserSettingsForm
    success_url = reverse_lazy('jscc-settings')
    success_message = "Settings saved."

    def get_object(self, queryset=None):
        obj, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return obj
