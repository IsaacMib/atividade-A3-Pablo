from django.test import TestCase
from io import StringIO
from django.core.management import call_command

class ImportNoticiasPloneApiCommandTests(TestCase):
    
    def test_command_output(self):
        print("Executando teste command_output")
        out = StringIO()
        call_command("import_noticias_plone_api", stdout=out)
        output = out.getvalue()
        print("Output do comando:", output)
        self.assertIn("Starting import of noticias from Plone API...", output)
        self.assertIn("Import completed successfully.", output)
