from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

class SlugTagMixin:
    """Behaviour shared by Project, CaseStudy and Post (no database fields)."""

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:120] or "item"
            candidate, n = base, 2
            model = type(self)
            while model.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{n}"
                n += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def __str__(self):
        return self.title


def _lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# Existing model (unchanged)
# ---------------------------------------------------------------------------

class Comment(models.Model):
    """Model to store user comments with name, email, comment text, and timestamp."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Show newest comments first

    def __str__(self):
        return f"Comment by {self.name} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# ---------------------------------------------------------------------------
# Public site content (managed in the Django admin)
# ---------------------------------------------------------------------------

class Project(SlugTagMixin, models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    client = models.CharField(max_length=120, blank=True)
    summary = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    key_results = models.TextField(blank=True, help_text="One result per line.")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated, e.g. AWS, Agile, Migration.")
    url = models.URLField(blank=True)
    featured = models.BooleanField(default=False, help_text="Show on the Home page.")
    published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    @property
    def result_list(self):
        return _lines(self.key_results)


class CaseStudy(SlugTagMixin, models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    client = models.CharField(max_length=120, blank=True)
    role = models.CharField(max_length=120, blank=True)
    summary = models.CharField(max_length=300)
    challenge = models.TextField(blank=True)
    approach = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    results = models.TextField(blank=True, help_text="One headline result per line.")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated.")
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name_plural = "case studies"

    def get_absolute_url(self):
        return reverse('case-study-detail', args=[self.slug])

    @property
    def result_list(self):
        return _lines(self.results)


class Post(SlugTagMixin, models.Model):
    """A Writing entry. The body is plain text; blank lines start new paragraphs."""
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated.")
    featured = models.BooleanField(default=False, help_text="Pin to the top of Writing.")
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def get_absolute_url(self):
        return reverse('writing-detail', args=[self.slug])


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject or 'No subject'}"


# ---------------------------------------------------------------------------
# JSCC - private, per-user job search command center
# ---------------------------------------------------------------------------

class Application(models.Model):
    WISHLIST, APPLIED, SCREENING, INTERVIEW, OFFER, REJECTED, WITHDRAWN = (
        'wishlist', 'applied', 'screening', 'interview', 'offer', 'rejected', 'withdrawn')
    STATUS_CHOICES = [
        (WISHLIST, 'Wishlist'),
        (APPLIED, 'Applied'),
        (SCREENING, 'Recruiter screen'),
        (INTERVIEW, 'Interviewing'),
        (OFFER, 'Offer'),
        (REJECTED, 'Rejected'),
        (WITHDRAWN, 'Withdrawn'),
    ]
    ACTIVE_STATUSES = (APPLIED, SCREENING, INTERVIEW)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    company = models.CharField(max_length=150)
    role_title = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WISHLIST)
    location = models.CharField(max_length=120, blank=True)
    job_url = models.URLField(blank=True)
    salary_range = models.CharField(max_length=80, blank=True)
    source = models.CharField(max_length=80, blank=True, help_text="Where you found it, e.g. LinkedIn or a referral.")
    applied_on = models.DateField(null=True, blank=True)
    next_step = models.CharField(max_length=200, blank=True)
    next_step_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.role_title} at {self.company}"


class NetworkContact(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='network_contacts')
    name = models.CharField(max_length=120)
    company = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    linkedin_url = models.URLField(blank=True)
    last_contacted = models.DateField(null=True, blank=True)
    follow_up_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class RoadmapItem(models.Model):
    NOW, NEXT, LATER = 'now', 'next', 'later'
    PHASE_CHOICES = [(NOW, 'Now'), (NEXT, 'Next'), (LATER, 'Later')]
    PLANNED, IN_PROGRESS, DONE = 'planned', 'in_progress', 'done'
    STATUS_CHOICES = [(PLANNED, 'Planned'), (IN_PROGRESS, 'In progress'), (DONE, 'Done')]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roadmap_items')
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    phase = models.CharField(max_length=10, choices=PHASE_CHOICES, default=NOW)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=PLANNED)
    target_date = models.DateField(null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


class ChecklistItem(models.Model):
    CATEGORY_CHOICES = [
        ('resume', 'Resume'),
        ('linkedin', 'LinkedIn'),
        ('portfolio', 'Portfolio'),
        ('networking', 'Networking'),
        ('interview', 'Interview prep'),
        ('admin', 'Admin'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checklist_items')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='admin')
    is_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jscc_settings')
    target_role = models.CharField(max_length=150, blank=True)
    target_locations = models.CharField(max_length=200, blank=True)
    weekly_application_goal = models.PositiveSmallIntegerField(default=5)
    weekly_outreach_goal = models.PositiveSmallIntegerField(default=3)
    email_reminders = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "user settings"

    def __str__(self):
        return f"Settings for {self.user}"
