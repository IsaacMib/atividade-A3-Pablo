from django.core.management import BaseCommand
from plone_migration.utils import GetToken, GetDataObject,GetFile
from noticias.models import NoticiasIndexPages, NoticiasPage
from wagtail.models import Site
import json
from django.utils.text import slugify
from datetime import datetime
import requests
from plone_migration.models import PloneImportedImage, PloneImportedFile
from django.core.files.base import ContentFile
import logging
import traceback
from django.utils import timezone
from PIL import Image as PilImage
from io import BytesIO
from wagtail.blocks import StreamValue

logger = logging.getLogger("plone_import")

def ImportNoticiasArquivos(token, item, noticia_import=False):
    response = GetDataObject(token, item)
    object = response.json()

    created_objs = []

    # Importa imagem
    if object.get("@type") == "Image" and "image" in object and "download" in object["image"]:
        image_url = object["image"]["download"]
        image_filename = object.get("id") or object["image"].get("filename") or object.get("title") or "imagem_plone.jpg"
        plone_node_id = object.get("UID")
        image_slug = object.get("id") or ""

        img_qs = PloneImportedImage.objects.filter(plone_node_id=plone_node_id)
        if img_qs.exists():
            logger.info(f"Imagem já importada: plone_node_id={plone_node_id}")
            if noticia_import:
                created_objs.append(img_qs.first())
        else:
            img_response = GetFile(image_url,token)
            logger.info(f"Resposta da requisição da imagem ({image_url}): status={img_response.status_code}, headers={img_response.headers}")
            logger.debug(f"Conteúdo da resposta da imagem ({image_url}): {img_response.content[:200]}")  # Loga os primeiros 200 bytes

            content_type = img_response.headers.get("Content-Type", "")
            if img_response.status_code == 200:
                # Ignora SVGs e arquivos não suportados
                if "svg" in content_type or str(image_filename).lower().endswith(".svg"):
                    logger.warning(f"Arquivo SVG ignorado: {image_filename} ({image_url})")
                    return created_objs
                try:
                    pil_image = PilImage.open(BytesIO(img_response.content))
                    pil_image.verify()  # Verifica se é uma imagem válida
                    pil_image = PilImage.open(BytesIO(img_response.content))  # Reabra para processar
                    img_io = BytesIO()
                    pil_image.save(img_io, format=pil_image.format, optimize=True, quality=70)
                    img_file = ContentFile(img_io.getvalue(), name=str(image_filename))
                except Exception as e:
                    logger.error(f"Erro ao processar imagem com Pillow: {e} ({image_filename})")
                    logger.error(f"URL da imagem: {image_url}")
                    logger.error(f"Primeiros bytes do arquivo: {img_response.content}")
                    return created_objs  # Não tente salvar imagem inválida

                img_obj = PloneImportedImage.objects.create(
                    plone_node_id=plone_node_id,
                    file=img_file,
                    title=image_filename,
                    slug_plone=image_slug,
                )
                created_objs.append(img_obj)

    # Importa arquivo (PDF, DOC, etc)
    if object.get("@type") == "File" and "file" in object and "download" in object["file"]:
        file_url = object["file"]["download"]
        file_filename = object["file"].get("filename", object.get("title", "arquivo_plone"))
        plone_node_id = object.get("UID")
        file_slug = object.get("id", None)

        file_qs = PloneImportedFile.objects.filter(plone_node_id=plone_node_id)
        if file_qs.exists():
            logger.info(f"Arquivo já importado: plone_node_id={plone_node_id}")
            if noticia_import:
                created_objs.append(file_qs.first())
        else:
            file_response = GetFile(file_url,token)
            if file_response.status_code == 200:
                file_content = ContentFile(file_response.content, name=file_filename)
                file_obj = PloneImportedFile.objects.create(
                    plone_node_id=plone_node_id,
                    file=file_content,
                    title=file_filename,
                    slug_plone=file_slug,
                )
                created_objs.append(file_obj)

    return created_objs


def ImportNoticias(token, item, noticias_index_page=None):
    response = GetDataObject(token, item)
    try:
        object = response.json()
    except Exception as e:
        logger.error(f"Erro ao decodificar JSON para item {item}: {e}")
        logger.error(f"Conteúdo bruto: {response.text if hasattr(response, 'text') else response}")
        logger.error(traceback.format_exc())
        return

    if not isinstance(object, dict):
        logger.error(f"Resposta inesperada do Plone para item {item}: {object}")
        logger.error(traceback.format_exc())
        return

    try:
        arquivos = object.get("items", [])
        imagens_para_adicionar = []
        arquivos_para_adicionar = []

        for arq in arquivos:
            try:
                print("process arq %s, %s" % (arq["@type"],arq["@id"]))
                objs_criados = ImportNoticiasArquivos(token, arq["@id"],noticia_import=True)
                for obj in objs_criados:
                    from plone_migration.models import PloneImportedImage, PloneImportedFile
                    if isinstance(obj, PloneImportedImage):
                        imagens_para_adicionar.append(obj)
                    elif isinstance(obj, PloneImportedFile):
                        arquivos_para_adicionar.append(obj)
            except Exception as e:
                logger.error(f"Erro ao importar arquivo associado: {e}")
                logger.error(f"Arquivo problemático: {json.dumps(arq, ensure_ascii=False, indent=2)}")
                logger.error(traceback.format_exc())

        # Cria a página de notícia se o index foi passado
        if noticias_index_page is not None:
            plone_node_id = object.get("UID")
            if NoticiasPage.objects.filter(plone_node_id=plone_node_id).exists():
                logger.info(f"Notícia já importada: plone_node_id={plone_node_id}")
            else:
                def parse_data(data_str):
                    if data_str:
                        try:
                            dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
                            if timezone.is_naive(dt):
                                dt = timezone.make_aware(dt, timezone.get_current_timezone())
                            return dt
                        except Exception:
                            return None
                    return None

                data_first_published = parse_data(object.get("created"))
                data_latest_revision = parse_data(object.get("modified"))
                data_publicacao = parse_data(object.get("effective"))

                images_stream = [
                    ('imagem', img) for img in imagens_para_adicionar
                ] if imagens_para_adicionar else []

                arquivos_stream = [
                    ('arquivo', arq) for arq in arquivos_para_adicionar
                ] if arquivos_para_adicionar else []

                body_migrated = ""
                text_field = object.get("text")
                if text_field and isinstance(text_field, dict):
                    body_migrated = text_field.get("data", "")

                # Só migra se body_migrated não for nulo ou vazio
                if not body_migrated:
                    logger.info(f"Notícia ignorada por body_migrated vazio: plone_node_id={plone_node_id}")
                    return

                nova_noticia = NoticiasPage(
                    title=object.get("title", "Sem título"),
                    slug=object.get("id", slugify(object.get("title", "sem-titulo"))),
                    plone_node_id=plone_node_id,
                    descricao=object.get("description", ""),
                    data_publicacao=data_publicacao,
                    body_migrated=body_migrated,
                    first_published_at=data_first_published,
                    latest_revision_created_at=data_latest_revision,
                )

                # Adiciona imagens e arquivos nos campos StreamField
                if images_stream:
                    nova_noticia.images = images_stream
                if arquivos_stream:
                    nova_noticia.arquivos = arquivos_stream

                noticias_index_page.add_child(instance=nova_noticia)
                revision = nova_noticia.save_revision()
                # Só publica se review_state for 'published'
                if object.get("review_state") == "published":
                    revision.publish()
                else:
                    # Garante que a página não fique live se não for publicada
                    if nova_noticia.live:
                        nova_noticia.unpublish()

    except Exception as e:
        logger.error(f"Erro ao importar notícia: {e}")
        logger.error(f"Notícia problematica: {json.dumps(object, ensure_ascii=False, indent=2)}")
        logger.error(traceback.format_exc())

def ListDataRaiz(token, url, noticias_index_page=None, qtd=1, limit=100):  
    response = GetDataObject(token, url)
    object = response.json()

    # Se o limite for negativo, não há limite
    if limit >= 0 and qtd > limit:
        return

    # Busca ou cria o NoticiasIndexPages
    if noticias_index_page is None:
        noticias_index_page = NoticiasIndexPages.objects.first()
        if not noticias_index_page:
            site = Site.objects.get(is_default_site=True)
            homepage = site.root_page.specific
            noticias_index_page = NoticiasIndexPages(
                title="Notícias",
                slug="noticias",
                introduction="Todas as notícias"
            )
            homepage.add_child(instance=noticias_index_page)
            noticias_index_page.save_revision().publish()  # <-- importante!
            noticias_index_page.refresh_from_db()  # <-- importante!

    itens = object["items"]

    for item in itens:
        #Se o limite for negativo, não há limite
        if limit >= 0 and qtd > limit:
            return
        print("%d process %s,%s" % (qtd, item["@type"], item["@id"]))
        qtd = qtd + 1
        if item["@type"] in ["Collection"]:
            continue
        if item["@type"] in ["Image"]:
            ImportNoticiasArquivos(token, item["@id"])
            continue
        # Aqui você pode criar as páginas filhas do tipo NoticiasPage usando noticias_index_page como pai
        ImportNoticias(token, item["@id"], noticias_index_page=noticias_index_page)
    if 'next' not in object['batching']:
        return

    ListDataRaiz(token, object['batching']['next'], noticias_index_page=noticias_index_page, qtd=qtd, limit=limit)


def importar_noticias(url, login, senha, limit=10):
    token = GetToken(url, login, senha)
    ListDataRaiz(token, url, limit=limit)

class Command(BaseCommand):
    help = "Import noticias from Plone API"

    def add_arguments(self, parser):
        parser.add_argument('--urlNoticias', type=str, required=True, help='URL da API de notícias do Plone')
        parser.add_argument('--login', type=str, required=True, help='Login do Plone')
        parser.add_argument('--senha', type=str, required=True, help='Senha do Plone')
        parser.add_argument('--limit', type=int, default=10, help='Limite de notícias para importar')

    def handle(self, *args, **options):
        url = options['urlNoticias']
        login = options['login']
        senha = options['senha']
        limit = options['limit']

        self.stdout.write("Starting import of noticias from Plone API..."+str(limit))
        try:
            importar_noticias(url, login, senha, limit)
            self.stdout.write(self.style.SUCCESS("Import completed successfully."))
        except Exception as e:
            import traceback
            logger.error(f"Erro durante importação: {e}")
            logger.error(traceback.format_exc())
            self.stdout.write(self.style.ERROR(f"An error occurred during import: {e}"))