from django.contrib import admin
from .models import LinkCabecalhoItemBlock

@admin.register(LinkCabecalhoItemBlock)
class LinkCabecalhoItemBlockAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'url', 'target')
    search_fields = ('titulo', 'url')
    list_filter = ('target',)
    ordering = ('titulo',)
    fieldsets = (
        (None, {
            'fields': ('titulo', 'url', 'target')
        }),
    )
