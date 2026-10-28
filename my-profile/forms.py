from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm, UserCreationForm,
)

from .models import (
    Application, ChecklistItem, Comment, ContactMessage, NetworkContact, RoadmapItem, UserSettings,
)


class BootstrapFormMixin:
    """Adds Bootstrap 5 classes to every widget so templates stay clean."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css = 'form-select'
            else:
                css = 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {css}".strip()


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        kwargs.setdefault('format', '%Y-%m-%d')
        super().__init__(**kwargs)


# --------------------------------------------------------------------------- existing
class CommentForm(forms.ModelForm):
    """Form for users to submit comments."""
    class Meta:
        model = Comment
        fields = ['name', 'email', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True,
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Comment',
                'rows': 4,
                'required': True,
            }),
        }


# --------------------------------------------------------------------------- public
class ContactForm(BootstrapFormMixin, forms.ModelForm):
    # Honeypot: real visitors never see or fill this in; simple bots do.
    website = forms.CharField(required=False, label='Website', widget=forms.TextInput(
        attrs={'tabindex': '-1', 'autocomplete': 'off'}))

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 6})}

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''


# --------------------------------------------------------------------------- JSCC
class ApplicationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Application
        fields = ['company', 'role_title', 'status', 'location', 'job_url', 'salary_range',
                  'source', 'applied_on', 'next_step', 'next_step_date', 'notes']
        widgets = {
            'applied_on': DateInput(),
            'next_step_date': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {'role_title': 'Role', 'job_url': 'Job posting URL', 'applied_on': 'Applied on'}


class NetworkContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = NetworkContact
        fields = ['name', 'company', 'title', 'email', 'phone', 'linkedin_url',
                  'last_contacted', 'follow_up_on', 'notes']
        widgets = {
            'last_contacted': DateInput(),
            'follow_up_on': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {'linkedin_url': 'LinkedIn URL', 'follow_up_on': 'Follow up on'}


class RoadmapItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = RoadmapItem
        fields = ['title', 'description', 'phase', 'status', 'target_date', 'sort_order']
        widgets = {'target_date': DateInput(), 'description': forms.Textarea(attrs={'rows': 3})}


class ChecklistItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ['title', 'category']
        widgets = {'title': forms.TextInput(attrs={'placeholder': 'Add a task...'})}


class UserSettingsForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ['target_role', 'target_locations', 'weekly_application_goal',
                  'weekly_outreach_goal', 'email_reminders']
        labels = {
            'weekly_application_goal': 'Weekly application goal',
            'weekly_outreach_goal': 'Weekly outreach goal',
            'email_reminders': 'Email me follow-up reminders',
        }


# --------------------------------------------------------------------------- accounts
class StyledAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    pass


class StyledPasswordResetForm(BootstrapFormMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(BootstrapFormMixin, SetPasswordForm):
    pass


class StyledPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')
