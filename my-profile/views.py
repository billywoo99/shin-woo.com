"""Public site views: Home, Experience, Projects, Case Studies, About, Contact, Writing."""
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .forms import CommentForm, ContactForm
from .models import CaseStudy, Comment, Post, Project


def collect_tags(items):
    """Sorted unique tags across a list of tagged objects."""
    return sorted({tag for item in items for tag in item.tag_list}, key=str.lower)


def filter_by_tag(items, tag):
    if not tag:
        return items
    return [item for item in items if tag in item.tag_list]


def published_posts():
    return Post.objects.filter(published=True, published_at__lte=timezone.now())


def hello(request):
    """Home view."""
    context = {
        'featured_projects': Project.objects.filter(published=True, featured=True)[:3],
        'featured_case_studies': CaseStudy.objects.filter(published=True, featured=True)[:2],
        'latest_posts': published_posts()[:3],
    }
    return render(request, "hello.html", context)


class ExperienceView(TemplateView):
    template_name = "experience.html"


class ProjectListView(ListView):
    template_name = "projects.html"
    context_object_name = "projects"

    def get_queryset(self):
        self.all_projects = list(Project.objects.filter(published=True))
        self.active_tag = self.request.GET.get('tag', '')
        return filter_by_tag(self.all_projects, self.active_tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = collect_tags(self.all_projects)
        context['active_tag'] = self.active_tag
        return context


class CaseStudyListView(ListView):
    template_name = "case_studies.html"
    context_object_name = "case_studies"

    def get_queryset(self):
        return CaseStudy.objects.filter(published=True)


class CaseStudyDetailView(DetailView):
    template_name = "case_study_detail.html"
    context_object_name = "case_study"

    def get_queryset(self):
        return CaseStudy.objects.filter(published=True)


class WritingListView(ListView):
    template_name = "writing.html"
    context_object_name = "posts"

    def get_queryset(self):
        self.all_posts = list(published_posts())
        self.active_tag = self.request.GET.get('tag', '')
        return filter_by_tag(self.all_posts, self.active_tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = collect_tags(self.all_posts)
        context['active_tag'] = self.active_tag
        return context


class WritingDetailView(DetailView):
    template_name = "writing_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return published_posts()


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thanks for reaching out - your message has been sent.")
        return super().form_valid(form)

    def form_invalid(self, form):
        if 'website' in form.errors:  # honeypot tripped: look successful, store nothing
            messages.success(self.request, "Thanks for reaching out - your message has been sent.")
            return redirect(self.success_url)
        return super().form_invalid(form)


def about(request):
    """About view with comment form and display."""
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks - your comment was submitted.")
            return redirect('about')  # Redirect after successful submission
    else:
        form = CommentForm()

    # Get all comments, ordered by most recent first
    comments = Comment.objects.all()

    context = {
        'form': form,
        'comments': comments,
    }
    return render(request, "about.html", context)
