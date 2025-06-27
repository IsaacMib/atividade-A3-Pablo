from django.core.management import BaseCommand
from plone_migration.utils import GetToken, GetDataObject

def ImportNoticiasArquivos(token, item):
    response = GetDataObject(token, item)
    object = response.json()

    #print("object arq: ", object)


def ImportNoticias(token, item):
    response = GetDataObject(token, item)
    object = response.json()

    # print("object: ", object)
    
    arquivos = object["items"]

    for arq in arquivos:
        print("process arq %s" % (arq["@type"]))
        # print("process img %s,%s, %s" % (arq["@id"], arq["title"], arq["@type"]))
        ImportNoticiasArquivos(token, arq["@id"])

def ListDataRaiz(token,url,qtd=1, limit=100):  
    response = GetDataObject(token,url)
    object = response.json()

    #Se o limite for negativo, não há limite
    if limit >= 0 and qtd > limit:
        return

    itens = object["items"]

    for item in itens:
        #Se o limite for negativo, não há limite
        if limit >= 0 and qtd > limit:
            return
        print("%d process %s,%s" % (qtd, item["@type"],item["@id"]))
        if item["@type"] in ["Collection"]:
            #   print("continue %s,%s, %s" % (item["@id"],item["title"],item["@type"]))
            continue
        if item["@type"] in ["Image"]:
            #print("process IMG %s,%s, %s" % (item["@id"],item["title"],item["@type"]))
            ImportNoticiasArquivos(token, item["@id"])
            continue
        # print("process %s,%s, %s" % (item["@id"],item["title"],item["@type"]))
        qtd=qtd+1
        ImportNoticias(token, item["@id"])
    if 'next' not in object['batching']:
        return
    
    ListDataRaiz(token, object['batching']['next'], qtd=qtd, limit=limit)


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
            self.stdout.write(self.style.ERROR(f"An error occurred during import: {e}"))