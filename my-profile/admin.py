from django.contrib import admin

from .models import (
    Application, CaseStudy, ChecklistItem, Comment, ContactMessage, NetworkContact,
    Post, Project, RoadmapItem, UserSettings,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'featured', 'published', 'sort_order')
    list_filter = ('published', 'featured')
    list_editable = ('featured', 'published', 'sort_order')
    search_fields = ('title', 'client', 'tags')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'featured', 'published', 'sort_order')
    list_filter = ('published', 'featured')
    list_editable = ('featured', 'published', 'sort_order')
    search_fields = ('title', 'client', 'tags')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'featured', 'published_at')
    list_filter = ('published', 'featured')
    search_fields = ('title', 'tags', 'body')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('name', 'email', 'subject', 'message')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'comment')


# JSCC data belongs to individual users; register for support/debugging only.
admin.site.register(Application)
admin.site.register(NetworkContact)
admin.site.register(RoadmapItem)
admin.site.register(ChecklistItem)
admin.site.register(UserSettings)
