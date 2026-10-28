"""
URL configuration for my-profile project.

Public pages live at the top level, the private Job Search Command Center (JSCC) under
/jscc/, and account pages under /accounts/. For more information see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path

from . import views, views_accounts as acct, views_jscc as jscc

handler404 = "my-profile.views_errors.not_found"
handler500 = "my-profile.views_errors.server_error"

public_patterns = [
    path("", views.hello, name="profile-hello"),
    path("experience/", views.ExperienceView.as_view(), name="experience"),
    path("projects/", views.ProjectListView.as_view(), name="projects"),
    path("case-studies/", views.CaseStudyListView.as_view(), name="case-study-list"),
    path("case-studies/<slug:slug>/", views.CaseStudyDetailView.as_view(), name="case-study-detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("writing/", views.WritingListView.as_view(), name="writing-list"),
    path("writing/<slug:slug>/", views.WritingDetailView.as_view(), name="writing-detail"),
]

account_patterns = [
    path("accounts/login/", acct.SiteLoginView.as_view(), name="login"),
    path("accounts/logout/", acct.SiteLogoutView.as_view(), name="logout"),
    path("accounts/register/", acct.RegisterView.as_view(), name="register"),
    path("accounts/profile/", acct.ProfileView.as_view(), name="profile"),
    path("accounts/password-change/", acct.SitePasswordChangeView.as_view(), name="password-change"),
    path("accounts/password-change/done/", acct.SitePasswordChangeDoneView.as_view(), name="password-change-done"),
    path("accounts/password-reset/", acct.SitePasswordResetView.as_view(), name="password-reset"),
    path("accounts/password-reset/done/", acct.SitePasswordResetDoneView.as_view(), name="password-reset-done"),
    path("accounts/reset/<uidb64>/<token>/", acct.SitePasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("accounts/reset/done/", acct.SitePasswordResetCompleteView.as_view(), name="password-reset-complete"),
]

jscc_patterns = [
    path("jscc/", jscc.DashboardView.as_view(), name="jscc-dashboard"),
    path("jscc/applications/", jscc.ApplicationListView.as_view(), name="jscc-application-list"),
    path("jscc/applications/new/", jscc.ApplicationCreateView.as_view(), name="jscc-application-create"),
    path("jscc/applications/export/", jscc.ApplicationExportView.as_view(), name="jscc-application-export"),
    path("jscc/applications/<int:pk>/edit/", jscc.ApplicationUpdateView.as_view(), name="jscc-application-update"),
    path("jscc/applications/<int:pk>/delete/", jscc.ApplicationDeleteView.as_view(), name="jscc-application-delete"),
    path("jscc/roadmap/", jscc.RoadmapListView.as_view(), name="jscc-roadmap-list"),
    path("jscc/roadmap/new/", jscc.RoadmapCreateView.as_view(), name="jscc-roadmap-create"),
    path("jscc/roadmap/<int:pk>/edit/", jscc.RoadmapUpdateView.as_view(), name="jscc-roadmap-update"),
    path("jscc/roadmap/<int:pk>/delete/", jscc.RoadmapDeleteView.as_view(), name="jscc-roadmap-delete"),
    path("jscc/checklist/", jscc.ChecklistView.as_view(), name="jscc-checklist"),
    path("jscc/checklist/<int:pk>/toggle/", jscc.ChecklistToggleView.as_view(), name="jscc-checklist-toggle"),
    path("jscc/checklist/<int:pk>/delete/", jscc.ChecklistDeleteView.as_view(), name="jscc-checklist-delete"),
    path("jscc/contacts/", jscc.ContactListView.as_view(), name="jscc-contact-list"),
    path("jscc/contacts/new/", jscc.ContactCreateView.as_view(), name="jscc-contact-create"),
    path("jscc/contacts/<int:pk>/edit/", jscc.ContactUpdateView.as_view(), name="jscc-contact-update"),
    path("jscc/contacts/<int:pk>/delete/", jscc.ContactDeleteView.as_view(), name="jscc-contact-delete"),
    path("jscc/settings/", jscc.SettingsView.as_view(), name="jscc-settings"),
]

urlpatterns = (
    public_patterns
    + account_patterns
    + jscc_patterns
    # The admin is where you add Projects, Case Studies and Writing, and read Contact messages.
    # Set ADMIN_URL (e.g. "my-secret-admin/") on Heroku to move it off the default address.
    + [path(settings.ADMIN_URL, admin.site.urls)]
)
