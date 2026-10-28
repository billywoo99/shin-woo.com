"""Load starter Projects and Case Study drafts based on the existing portfolio page.

Usage:  python manage.py seed_content
Safe to run more than once: items are matched by title and never overwritten.
Case studies are created as unpublished drafts so nothing half-finished goes live.
"""
from django.core.management.base import BaseCommand

from ...models import CaseStudy, Project

PROJECTS = [
    dict(title="Enterprise Cloud Migration", client="Google (under IBM)", sort_order=10, featured=True,
         summary="Led the migration of enterprise applications to AWS, ensuring minimal downtime and data integrity.",
         key_results="Up to 25% time savings for end-users.", tags="AWS, Cloud migration"),
    dict(title="Internal Enterprise Applications Migration", client="Google (under IBM)", sort_order=20, featured=True,
         summary="Managed the product lifecycle for the migration and support transition of 9 Google internal enterprise applications, focused on user experience and supportability.",
         key_results="18% reduction in support tickets\n12% decrease in support response time\n20% improvement in customer satisfaction",
         tags="Migration, Product management, Support"),
    dict(title="\"Above Wing\" Cloud Transformation", client="Delta Airlines (under IBM)", sort_order=30, featured=True,
         summary="Drove the cloud transformation of the \"Above Wing\" application from concept validation to a successful AWS hybrid cloud launch, serving as Agile Scrum Master.",
         key_results="20% improvement in user productivity\n20% faster, more efficient application, delivered on time",
         tags="AWS, Agile, Scrum"),
    dict(title="Dynamics CRM Customization", client="Boeing (Contracted)", sort_order=40, featured=False,
         summary="Led technical discovery and requirements definition, then customized Dynamics CRM using .NET (C#, JavaScript) with cross-functional partners including Microsoft.",
         key_results="15% improvement in project efficiency, with measurable user time savings", tags=".NET, CRM"),
    dict(title="NowAssist AI Implementation", client="Energy Company (under IBM)", sort_order=50, featured=False, published=False,
         summary="[Add a summary - the live site currently repeats the Above Wing description for this project.]",
         key_results="", tags="AI"),
]

CASE_STUDIES = [
    dict(title="Moving Google's internal enterprise apps to a supportable platform", client="Google (under IBM)",
         role="Product & Project Manager", sort_order=10, featured=True, published=False,
         summary="Managed the product lifecycle for migrating and transitioning support of 9 internal enterprise applications.",
         challenge="[Add: what was broken or risky about the starting point?]",
         approach="Managed the product lifecycle for the migration and support transition, with a focus on user experience and supportability.\n\n[Add: how you structured the work, who you aligned, and the key decisions.]",
         outcome="[Add: what changed for users and the support team.]",
         results="18% reduction in support tickets\n12% decrease in support response time\n20% improvement in customer satisfaction",
         tags="Migration, Product management"),
    dict(title="Delta \"Above Wing\": from concept to AWS hybrid cloud", client="Delta Airlines (under IBM)",
         role="Project Manager & Scrum Master", sort_order=20, featured=True, published=False,
         summary="Led the cloud transformation of the \"Above Wing\" application from concept validation to launch.",
         challenge="[Add: the business problem the transformation had to solve.]",
         approach="Led the product development process from concept validation to an AWS hybrid cloud launch. Served as Agile Scrum Master, overseeing requirements definition, training, migration, and testing.\n\n[Add: key trade-offs and how risks were managed.]",
         outcome="[Add: how the launch went and what happened afterwards.]",
         results="20% improvement in user productivity\n20% faster, more efficient application\nDelivered on time",
         tags="AWS, Agile, Cloud"),
]


class Command(BaseCommand):
    help = "Create starter projects and draft case studies if they do not exist yet."

    def handle(self, *args, **options):
        created = 0
        for data in PROJECTS:
            _, was_created = Project.objects.get_or_create(title=data["title"], defaults=data)
            created += was_created
        for data in CASE_STUDIES:
            _, was_created = CaseStudy.objects.get_or_create(title=data["title"], defaults=data)
            created += was_created
        self.stdout.write(self.style.SUCCESS(f"Done. {created} new item(s) created."))
