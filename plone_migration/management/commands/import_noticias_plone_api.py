from django.core.management import BaseCommand

def importar_noticias():
    # lógica real
    pass

class Command(BaseCommand):
    help = "Import noticias from Plone API"

    def handle(self, *args, **options):
        self.stdout.write("Starting import of noticias from Plone API...")
        try:
            importar_noticias()
            self.stdout.write(self.style.SUCCESS("Import completed successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during import: {e}"))