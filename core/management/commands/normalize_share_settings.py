from django.core.management.base import BaseCommand, CommandError
from core.models import SiteSettings
import json

class Command(BaseCommand):
    help = (
        "Normalize 'compartilhar_rede_social' in SiteSettings to a list-of-strings format.\n"
        "By default performs a dry run and prints proposed changes. Use --apply to persist changes."
    )

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Persist changes to the database')

    def handle(self, *args, **options):
        apply = options['apply']
        SiteSettingsModel = SiteSettings
        instances = SiteSettingsModel.objects.all()
        if not instances:
            self.stdout.write('No SiteSettings instances found.')
            return

        for ss in instances:
            original = ss.compartilhar_rede_social

            def _serialize_streamfield(sf):
                out = []
                try:
                    for bloco in sf:
                        bt = getattr(bloco, 'block_type', None) or getattr(bloco, 'type', None)
                        try:
                            val = bloco.value
                        except Exception:
                            # fallback: repr
                            val = repr(bloco)

                        # Normalize StructValue/ListValue to primitives where possible
                        if hasattr(val, 'items'):
                            try:
                                val = {k: (getattr(v, 'value', v) if not isinstance(v, (list, dict)) else v) for k, v in val.items()}
                            except Exception:
                                val = repr(val)
                        elif isinstance(val, (list, tuple)):
                            new = []
                            for it in val:
                                if hasattr(it, 'value'):
                                    new.append(getattr(it, 'value'))
                                else:
                                    new.append(it)
                            val = new
                        out.append({'type': bt, 'value': val})
                except Exception:
                    return repr(sf)
                return out
            # Normalize into a list of strings
            normalized = []
            changed = False

            try:
                for bloco in original:
                    inner = bloco.value
                    # If inner is dict with key 'redes' (our preferred structure)
                    if isinstance(inner, dict) and 'redes' in inner:
                        for nome in inner.get('redes') or []:
                            if nome and nome not in normalized:
                                normalized.append(nome)
                    else:
                        # inner might be a list of struct items or strings
                        try:
                            for item in inner:
                                if hasattr(item, 'value') and isinstance(item.value, dict):
                                    # legacy struct format: item.value may have 'nome'
                                    nome = item.value.get('nome')
                                    if nome and nome not in normalized:
                                        normalized.append(nome)
                                elif isinstance(item, str):
                                    if item and item not in normalized:
                                        normalized.append(item)
                        except Exception:
                            # if not iterable, try single string
                            if isinstance(inner, str) and inner not in normalized:
                                normalized.append(inner)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Unable to parse SiteSettings id={ss.pk}: {e}'))
                continue

            # Build a representation for display
            self.stdout.write('\n---')
            self.stdout.write(f'SiteSettings id={ss.pk} (site={getattr(ss, "site_id", None)})')
            self.stdout.write('Original:')
            try:
                self.stdout.write(json.dumps(_serialize_streamfield(original), ensure_ascii=False, indent=2))
            except Exception:
                self.stdout.write(repr(original))
            self.stdout.write('Normalized list-of-strings:')
            self.stdout.write(str(normalized))

            if apply:
                # Persist: store as a StreamField with a single StructBlock matching ListRedesSociais
                # The expected JSON structure varies; we will set compartilhar_rede_social to a
                # list containing one object with key 'redes' mapping to the list of strings.
                try:
                    ss.compartilhar_rede_social = [{'type': 'redes_compartilhar', 'value': {'redes': normalized}}]
                    ss.save()
                    self.stdout.write(self.style.SUCCESS(f'Applied normalization for SiteSettings id={ss.pk}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to save SiteSettings id={ss.pk}: {e}'))
            else:
                self.stdout.write('Dry run: no changes applied. Use --apply to persist.')
        self.stdout.write('\nDone.')
