# Generated manually to rename descricao field
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linhasdotempo', '0003_alter_linhadotempoindex_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cardlinhadotempopage',
            old_name='descricao',
            new_name='descricao_linha_do_tempo',
        ),
    ]
