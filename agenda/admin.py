from django.contrib import admin
from .models import AgendaDoDiaPage, AgendaPage

# Register your models here.

@admin.register(AgendaDoDiaPage)
class AgendaDoDiaPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'habilitar_recorrencia', 'tipo_recorrencia', 'intervalo_recorrencia']
    list_filter = ['habilitar_recorrencia', 'tipo_recorrencia', 'date']
    search_fields = ['title', 'nome_autoridade']
    readonly_fields = ['path', 'url_path']
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['title', 'slug', 'date']
        }),
        ('Recorrência', {
            'fields': ['habilitar_recorrencia', 'tipo_recorrencia', 'intervalo_recorrencia', 'data_final_recorrencia']
        }),
        ('Conteúdo', {
            'fields': ['compromissos', 'nome_autoridade', 'local_padrao']
        }),
        ('Informações do Sistema', {
            'fields': ['path', 'url_path'],
            'classes': ['collapse']
        })
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content_type')
