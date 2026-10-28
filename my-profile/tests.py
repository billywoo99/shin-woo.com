from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from datetime import timedelta

from django.utils import timezone

from .models import Application, CaseStudy, ChecklistItem, ContactMessage, Post, Project

PUBLIC_URLS = ['profile-hello', 'experience', 'projects', 'case-study-list', 'about', 'contact', 'writing-list']
JSCC_URLS = ['jscc-dashboard', 'jscc-application-list', 'jscc-application-create', 'jscc-roadmap-list',
             'jscc-checklist', 'jscc-contact-list', 'jscc-settings']


class PublicPageTests(TestCase):
    def test_public_pages_load(self):
        for name in PUBLIC_URLS:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_only_published_items_are_visible(self):
        Project.objects.create(title="Live project", summary="s", published=True)
        Project.objects.create(title="Hidden project", summary="s", published=False)
        CaseStudy.objects.create(title="Draft study", summary="s", published=False)
        Post.objects.create(title="Future post", body="b", published=True,
                            published_at=timezone.now() + timedelta(days=3))
        self.assertContains(self.client.get(reverse('projects')), "Live project")
        self.assertNotContains(self.client.get(reverse('projects')), "Hidden project")
        self.assertNotContains(self.client.get(reverse('case-study-list')), "Draft study")
        self.assertNotContains(self.client.get(reverse('writing-list')), "Future post")

    def test_contact_form_saves_message_and_blocks_honeypot(self):
        data = {'name': 'Ada', 'email': 'ada@example.com', 'subject': 'Hi', 'message': 'Hello there'}
        self.client.post(reverse('contact'), data)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.client.post(reverse('contact'), {**data, 'website': 'http://spam.example'})
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_slug_is_generated_and_unique(self):
        a = Project.objects.create(title="Same title", summary="s")
        b = Project.objects.create(title="Same title", summary="s")
        self.assertNotEqual(a.slug, b.slug)


class JsccAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user('alice', 'alice@example.com', 'pass-12345-xyz')
        self.bob = User.objects.create_user('bob', 'bob@example.com', 'pass-12345-xyz')

    def test_jscc_requires_login(self):
        for name in JSCC_URLS:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response['Location'])

    def test_jscc_pages_load_when_logged_in(self):
        self.client.force_login(self.alice)
        for name in JSCC_URLS:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_users_cannot_see_or_edit_each_others_data(self):
        app = Application.objects.create(owner=self.bob, company="BobCorp", role_title="Engineer")
        self.client.force_login(self.alice)
        self.assertNotContains(self.client.get(reverse('jscc-application-list')), "BobCorp")
        self.assertEqual(self.client.get(reverse('jscc-application-update', args=[app.pk])).status_code, 404)
        item = ChecklistItem.objects.create(owner=self.bob, title="Bob task")
        self.assertEqual(self.client.post(reverse('jscc-checklist-toggle', args=[item.pk])).status_code, 404)

    def test_checklist_toggle(self):
        item = ChecklistItem.objects.create(owner=self.alice, title="Task")
        self.client.force_login(self.alice)
        self.client.post(reverse('jscc-checklist-toggle', args=[item.pk]))
        item.refresh_from_db()
        self.assertTrue(item.is_done)


class AccountTests(TestCase):
    def test_account_pages_load(self):
        for name in ['login', 'register', 'password-reset', 'password-reset-done', 'password-reset-complete']:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    @override_settings(ALLOW_REGISTRATION=True)
    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser', 'email': 'new@example.com',
            'password1': 'a-Strong-pass-123', 'password2': 'a-Strong-pass-123'})
        self.assertRedirects(response, reverse('jscc-dashboard'), fetch_redirect_response=False)
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())

    @override_settings(ALLOW_REGISTRATION=False)
    def test_registration_can_be_closed(self):
        self.client.post(reverse('register'), {
            'username': 'blocked', 'email': 'b@example.com',
            'password1': 'a-Strong-pass-123', 'password2': 'a-Strong-pass-123'})
        self.assertFalse(get_user_model().objects.filter(username='blocked').exists())
