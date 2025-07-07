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
from bs4 import BeautifulSoup

logger = logging.getLogger("plone_import")

def ImportNoticiasArquivos(token, item, noticia_import=False, urlBase=None):
    response = GetDataObject(token, item)
    object = response.json()

    created_objs = []

    # Importa imagem
    if object.get("@type") == "Image" and "image" in object and "download" in object["image"]:
        img_obj = baixar_e_criar_imagem(token, object)
        if img_obj and noticia_import:
            created_objs.append(img_obj)

    # Importa arquivo (PDF, DOC, etc)
    if object.get("@type") == "File" and "file" in object and "download" in object["file"]:
        file_obj = baixar_e_criar_arquivo(token, object)
        if file_obj and noticia_import:
            created_objs.append(file_obj)

    return created_objs

def ImportNoticias(token, item, noticias_index_page=None, urlBase=None):
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
                objs_criados = ImportNoticiasArquivos(token, arq["@id"], noticia_import=True, urlBase=urlBase)
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


                body_migrated = ""
                text_field = object.get("text")
                if text_field and isinstance(text_field, dict):
                    body_migrated = text_field.get("data", "")

                # Só migra se body_migrated não for nulo ou vazio
                if not body_migrated:
                    logger.info(f"Notícia ignorada por body_migrated vazio: plone_node_id={plone_node_id}")
                    return

                # Cria o StreamField para o body com o bloco paragraph_block
                body_stream = [('paragraph_block', body_migrated)]

                nova_noticia = NoticiasPage(
                    title=object.get("title", "Sem título"),
                    slug=object.get("id", slugify(object.get("title", "sem-titulo"))),
                    plone_node_id=plone_node_id,
                    descricao=object.get("description", ""),
                    data_publicacao=data_publicacao,
                    body_migrated=body_migrated,
                    body=body_stream,  # <-- Adiciona o conteúdo no StreamField
                    first_published_at=data_first_published,
                    latest_revision_created_at=data_latest_revision,
                )

                # Substitui os links das imagens no body_migrated pelos links das imagens importadas
                body_migrated_atualizado, imagens_encontradas = substituir_links_imagens(token, body_migrated, imagens_para_adicionar, urlBase)
                # Atualiza também o campo body (StreamField) com o HTML atualizado
                nova_noticia.body, arquivos_encontrados = gerar_blocks_body(body_migrated_atualizado,token=token, urlBase=urlBase)

                # Adiciona imagens encontradas pelo UID, se ainda não estiverem em imagens_para_adicionar
                for img in imagens_encontradas:
                    if img not in imagens_para_adicionar:
                        imagens_para_adicionar.append(img)
                
                for arquivo in arquivos_encontrados:
                    if arquivo not in arquivos_para_adicionar:
                        arquivos_para_adicionar.append(arquivo)

                images_stream = [
                    ('imagem', img) for img in imagens_para_adicionar
                ] if imagens_para_adicionar else []

                arquivos_stream = [
                    ('arquivo', arq) for arq in arquivos_para_adicionar
                ] if arquivos_para_adicionar else []

                # Adiciona imagens e arquivos nos campos StreamField
                if images_stream:
                    nova_noticia.images = images_stream
                if arquivos_stream:
                    nova_noticia.arquivos = arquivos_stream

                # Define slideshow_imagens como True se houver 2 ou mais imagens
                nova_noticia.slideshow_imagens = len(imagens_para_adicionar) >= 2

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

def ListDataRaiz(token, url, noticias_index_page=None, qtd=1, limit=100, urlBase=None):  
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
            ImportNoticiasArquivos(token, item["@id"], urlBase=urlBase)
            continue
        # Aqui você pode criar as páginas filhas do tipo NoticiasPage usando noticias_index_page como pai
        ImportNoticias(token, item["@id"], noticias_index_page=noticias_index_page, urlBase=urlBase)
    if 'next' not in object['batching']:
        return

    ListDataRaiz(token, object['batching']['next'], noticias_index_page=noticias_index_page, qtd=qtd, limit=limit, urlBase=urlBase)


def importar_noticias(url, login, senha, limit=10, urlBase=None):
    token = GetToken(url, login, senha)
    ListDataRaiz(token, url, limit=limit, urlBase=urlBase)

class Command(BaseCommand):
    help = "Import noticias from Plone API"

    def add_arguments(self, parser):
        parser.add_argument('--urlNoticias', type=str, required=True, help='URL da API de notícias do Plone')
        parser.add_argument('--login', type=str, required=True, help='Login do Plone')
        parser.add_argument('--senha', type=str, required=True, help='Senha do Plone')
        parser.add_argument('--limit', type=int, default=10, help='Limite de notícias para importar')
        parser.add_argument('--urlBase', type=str, required=True, help='URL base para compor links absolutos das imagens')

    def handle(self, *args, **options):
        url = options['urlNoticias']
        login = options['login']
        senha = options['senha']
        limit = options['limit']
        urlBase = options['urlBase']

        self.stdout.write("Starting import of noticias from Plone API..."+str(limit))
        try:
            importar_noticias(url, login, senha, limit, urlBase)
            self.stdout.write(self.style.SUCCESS("Import completed successfully."))
        except Exception as e:
            logger.error(f"Erro durante importação: {e}")
            logger.error(traceback.format_exc())
            self.stdout.write(self.style.ERROR(f"An error occurred during import: {e}"))

def substituir_links_imagens(token, body_migrated, imagens_para_adicionar, urlBase=None):
    """
    Substitui os links das imagens no HTML body_migrated pelos links das imagens importadas,
    mantendo o tamanho original da imagem (width e height).
    Antes de fazer GetFile, chama GetDataObject para pegar o link de download correto.
    Se não houver campo de download, faz o fallback via requests.get.
    Se a imagem já existir na base (pelo UID), retorna o objeto para ser adicionado posteriormente na NoticiaPage.
    Se o src contiver @@images, remove o path a partir de @@images para passar ao GetDataObject.
    Só processa imagens cujo src começa com a urlBase.
    """
    if not body_migrated or not urlBase:
        return body_migrated, []

    imagens_encontradas = []

    soup = BeautifulSoup(body_migrated, "html.parser")
    for img_tag in soup.find_all("img"):
        img_src = img_tag.get("src", "")
        img_alt = img_tag.get("alt", "")

        # Só processa imagens que tenham a mesma urlBase
        if not img_src.startswith(urlBase):
            continue

        # Ajusta o parâmetro para GetDataObject caso haja @@images no src
        getdata_url = img_src
        if "@@images" in img_src:
            getdata_url = img_src.split("/@@images")[0]

        try:
            response = GetDataObject(token, getdata_url)
            obj = response.json()

            # Não processa se o tipo for NotFound
            if obj.get("@type") == "NotFound":
                logger.warning(f"Imagem não encontrada para URL: {getdata_url}")
                continue

            plone_uid = obj.get("UID")
            img_obj = None

            # widthImgOriginal = None
            # heightImgOriginal = None

            # # O tamanho vai ser sempre da imagem original.
            # resp = requests.get(img_src, timeout=30)
            # if resp.status_code == 200:
            #     with PilImage.open(BytesIO(resp.content)) as pil_img:
            #         widthImgOriginal, heightImgOriginal = pil_img.size

            # Verifica se já existe na base pelo UID
            if plone_uid:
                img_qs = PloneImportedImage.objects.filter(plone_node_id=plone_uid)
                if img_qs.exists():
                    img_obj = img_qs.first()
                    imagens_encontradas.append(img_obj)

            # Se não encontrou pelo UID, tenta pelo título
            if not img_obj:
                for img in imagens_para_adicionar:
                    if img.title in img_src or img.title in img_alt:
                        img_obj = img
                        imagens_encontradas.append(img_obj)
                        break

            if not img_obj:
                img_obj = baixar_e_criar_imagem(token, obj)
                if img_obj:
                    imagens_encontradas.append(img_obj)

            # Substitui o src pelo novo e adiciona width/height se disponíveis
            if img_obj:
                # Determina o formato pela classe
                img_class = img_tag.get("class", [])
                if isinstance(img_class, str):
                    img_class = img_class.split()
                img_class_str = " ".join(img_class).lower()
                if "right" in img_class_str:
                    img_format = "right"
                elif "left" in img_class_str:
                    img_format = "left"
                else:
                    img_format = "fullwidth"
                # Monta o <embed ... /> no padrão Wagtail
                embed_tag = soup.new_tag(
                    "embed",
                    embedtype="image",
                    format=img_format,
                    id=str(img_obj.id),
                    alt=img_tag.get("alt", "")
                )
                # Substitui o <img> pelo <embed>
                img_tag.replace_with(embed_tag)

        except Exception as e:
            logger.warning(f"Não foi possível processar imagem {getdata_url}: {e}")
            logger.error(traceback.format_exc())

    return str(soup), imagens_encontradas

def gerar_blocks_body(html, token=None, urlBase=None):
    """
    Recebe o HTML processado pelo substituir_links_imagens e retorna uma lista de blocks
    para ser usada no campo body do NoticiasPage.
    Agrupa todos os <p> (ou <div>) em paragraph_block, mantendo a ordem do HTML.
    Quando encontrar um <iframe> (direto ou dentro de <p>), cria um bloco separado do tipo iframe_block,
    adiciona o que estava no buffer como paragraph_block e continua o processo.
    Também processa links para arquivos, baixando e substituindo o href pelo novo arquivo.
    Retorna (blocks, arquivos_encontrados)
    """
    blocks = []
    arquivos_encontrados = []
    soup = BeautifulSoup(html, "html.parser")
    buffer = []

    def flush_paragraph():
        content = "".join(buffer).strip()
        if content:
            blocks.append(('paragraph_block', content))
        buffer.clear()

    def process_link_tag(a_tag):
        href = a_tag.get("href", "")
        if not href or not urlBase or not href.startswith(urlBase):
            return None
        # Verifica se é um arquivo (extensão comum)
        if any(href.lower().endswith(ext) for ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar", ".csv", ".txt"]):
            try:
                # Busca metadados do arquivo no Plone
                getdata_url = href
                response = GetDataObject(token, getdata_url)
                obj = response.json()
                if obj.get("@type") == "NotFound":
                    logger.warning(f"Arquivo não encontrado para URL: {getdata_url}")
                    return None
                file_obj = baixar_e_criar_arquivo(token, obj)
                if file_obj:
                    arquivos_encontrados.append(file_obj)
                    # Atualiza o href para o novo arquivo (ajuste conforme sua lógica de URL)
                    a_tag['href'] = file_obj.file.url if hasattr(file_obj.file, 'url') else ""
                    return file_obj
            except Exception as e:
                logger.warning(f"Não foi possível processar arquivo {href}: {e}")
                logger.error(traceback.format_exc())
        return None

    # Percorre todos os elementos do body (ou do soup se não houver body)
    elements = soup.body.contents if soup.body else soup.contents
    for elem in elements:
        # Se for uma tag <p> ou <div>
        if getattr(elem, 'name', None) in ['p', 'div']:
            # Processa todos os <a> filhos desse parágrafo/div
            for a_tag in elem.find_all("a"):
                process_link_tag(a_tag)
            # Verifica se há <iframe> dentro do <p> ou <div>
            iframe = elem.find('iframe')
            if iframe:
                iframe_html = str(iframe)
                elem_iframe_removed = elem.decode_contents().replace(iframe_html, "")
                if elem_iframe_removed.strip():
                    buffer.append(f"<{elem.name}>{elem_iframe_removed}</{elem.name}>")
                flush_paragraph()
                # Cria bloco do tipo iframe_block
                iframe_attrs = iframe.attrs
                blocks.append((
                    'iframe_block',
                    {
                        'url': iframe_attrs.get('src', ''),
                        'width': iframe_attrs.get('width', '100%'),
                        'height': iframe_attrs.get('height', '400'),
                        'allowfullscreen': iframe_attrs.get('allowfullscreen', True),
                    }
                ))
            else:
                buffer.append(str(elem))
        # Se for uma tag <a> fora de <p> ou <div>
        elif getattr(elem, 'name', None) == 'a':
            process_link_tag(elem)
            buffer.append(str(elem))
        # Se for uma tag <iframe> fora de <p> ou <div>
        elif getattr(elem, 'name', None) == 'iframe':
            flush_paragraph()
            iframe_attrs = elem.attrs
            blocks.append((
                'iframe_block',
                {
                    'url': iframe_attrs.get('src', ''),
                    'width': iframe_attrs.get('width', '100%'),
                    'height': iframe_attrs.get('height', '400'),
                    'allowfullscreen': iframe_attrs.get('allowfullscreen', True),
                }
            ))
        # Se for apenas texto fora de <p> ou <div>
        elif isinstance(elem, str):
            if elem.strip():
                buffer.append(elem)
        # Outras tags (ex: <embed>), também podem ser incluídas no buffer
        elif getattr(elem, 'name', None):
            # Se for <a> aninhado em outro tipo de tag, processa também
            if elem.name == 'a':
                process_link_tag(elem)
            buffer.append(str(elem))

    # Adiciona o que restou no buffer como paragraph_block
    flush_paragraph()
    return blocks, arquivos_encontrados

def baixar_e_criar_imagem(token, obj, image_url=None, image_filename=None, plone_node_id=None, image_slug=None, width=None, height=None):
    """
    Faz o download da imagem, processa com Pillow e cria um PloneImportedImage.
    Retorna o objeto criado ou None.
    """
    if not image_url:
        image_url = obj.get("image", {}).get("download")
    if not image_filename:
        image_filename = obj.get("id") or obj.get("title") or "imagem_plone.jpg"
    if not plone_node_id:
        plone_node_id = obj.get("UID")
    if not image_slug:
        image_slug = obj.get("id") or ""

    img_qs = PloneImportedImage.objects.filter(plone_node_id=plone_node_id)
    if img_qs.exists():
        return img_qs.first()

    img_response = GetFile(image_url, token)
    logger.info(f"Resposta da requisição da imagem ({image_url}): status={img_response.status_code}, headers={img_response.headers}")
    logger.debug(f"Conteúdo da resposta da imagem ({image_url}): {img_response.content[:200]}")

    content_type = img_response.headers.get("Content-Type", "")
    if img_response.status_code == 200:
        if "svg" in content_type or str(image_filename).lower().endswith(".svg"):
            logger.warning(f"Arquivo SVG ignorado: {image_filename} ({image_url})")
            return None
        try:
            pil_image = PilImage.open(BytesIO(img_response.content))
            pil_image.verify()
            pil_image = PilImage.open(BytesIO(img_response.content))
            # Redimensiona se width/height forem passados
            # if width and height:
            #     pil_image = pil_image.resize((width, height), PilImage.LANCZOS)
            img_io = BytesIO()
            pil_image.save(img_io, format=pil_image.format, optimize=True, quality=70)
            img_file = ContentFile(img_io.getvalue(), name=str(image_filename))
        except Exception as e:
            logger.error(f"Erro ao processar imagem com Pillow: {e} ({image_filename})")
            logger.error(f"URL da imagem: {image_url}")
            return None

        return PloneImportedImage.objects.create(
            plone_node_id=plone_node_id,
            file=img_file,
            title=image_filename,
            slug_plone=image_slug,
        )
    return None

def baixar_e_criar_arquivo(token, obj, file_url=None, file_filename=None, plone_node_id=None, file_slug=None):
    """
    Faz o download do arquivo e cria um PloneImportedFile.
    Retorna o objeto criado ou None.
    """
    if not file_url:
        file_url = obj.get("file", {}).get("download")
    if not file_filename:
        file_filename = obj.get("file", {}).get("filename") or obj.get("title", "arquivo_plone")
    if not plone_node_id:
        plone_node_id = obj.get("UID")
    if not file_slug:
        file_slug = obj.get("id", None)

    file_qs = PloneImportedFile.objects.filter(plone_node_id=plone_node_id)
    if file_qs.exists():
        return file_qs.first()

    file_response = GetFile(file_url, token)
    if file_response.status_code == 200:
        file_content = ContentFile(file_response.content, name=file_filename)
        return PloneImportedFile.objects.create(
            plone_node_id=plone_node_id,
            file=file_content,
            title=file_filename,
            slug_plone=file_slug,
        )
    return None
