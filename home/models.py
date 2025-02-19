from django.db import models

from wagtail.models import Page


class HomePage(Page):
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        context['loop_times'] = range(0, 60)
        return context
