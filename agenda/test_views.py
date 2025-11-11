from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, datetime
import json

from wagtail.models import Page, Site
from agenda.models import AgendaPage, AgendaDoDiaPage
from home.models import HomePage


class AgendaAPIViewsTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """Setup executado uma vez para toda a classe de teste"""
        # Criar usuário para autenticação
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        
        # Garante que existe uma página root
        root = Page.get_first_root_node()
        if not root:
            root = Page.add_root(title="Root", slug="root")
        
        cls.root_page = root
        
        cls.home_page = HomePage(title="Home Test Views", slug="home-test-views")
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        
        # Configurar Site para apontar para home_page
        try:
            cls.site = Site.objects.get(is_default_site=True)
            cls.site.root_page = cls.home_page
            cls.site.save()
        except Site.DoesNotExist:
            cls.site = Site.objects.create(
                hostname='testserver',
                port=80,
                root_page=cls.home_page,
                is_default_site=True,
                site_name="Test Site"
            )
        
        cls.agenda_page = AgendaPage(
            title="Agenda da Presidência API",
            slug="agenda-presidencia-api",
            local_padrao="Palácio da Presidência"
        )
        cls.home_page.add_child(instance=cls.agenda_page)
        cls.agenda_page.save_revision().publish()
        
        # Agenda normal para teste com compromissos
        cls.agenda_normal = AgendaDoDiaPage(
            title="Agenda Normal API",
            slug="agenda-normal-api",
            date=date(2025, 11, 15),
            habilitar_recorrencia=False,
            compromissos=[
                {
                    'type': 'compromisso',
                    'value': {
                        'title': 'Reunião Teste Normal',
                        'nome_autoridade': 'Presidente',
                        'inicio': '09:00',
                        'termino': '10:00',
                        'local': 'Sala de Reuniões',
                        'pauta': 'Pauta de teste'
                    }
                }
            ]
        )
        cls.agenda_page.add_child(instance=cls.agenda_normal)
        cls.agenda_normal.save_revision().publish()
        
        # Agenda recorrente para teste com compromissos
        cls.agenda_recorrente = AgendaDoDiaPage(
            title="Agenda Recorrente API",
            slug="agenda-recorrente-api",
            date=date(2025, 11, 11),
            habilitar_recorrencia=True,
            tipo_recorrencia='months',
            intervalo_recorrencia=1,
            data_final_recorrencia=date(2025, 12, 31),
            compromissos=[
                {
                    'type': 'compromisso',
                    'value': {
                        'title': 'Reunião Teste Recorrente',
                        'nome_autoridade': 'Presidente',
                        'inicio': '14:00',
                        'termino': '15:00',
                        'local': 'Gabinete',
                        'pauta': 'Pauta recorrente'
                    }
                }
            ]
        )
        cls.agenda_page.add_child(instance=cls.agenda_recorrente)
        cls.agenda_recorrente.save_revision().publish()
        
    def setUp(self):
        """Setup executado antes de cada teste"""
        # Fazer login do usuário
        self.client.force_login(self.user)
    
    def test_agenda_page_get_datas_periodo_sucesso(self):
        """Testa endpoint GET datas-periodo com sucesso"""
        url = f'{self.agenda_page.url}datas-periodo/'
        response = self.client.get(url, {
            'start': '2025-11-01',
            'end': '2026-01-31'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verifica estrutura da resposta
        self.assertIn('datas', data)
        self.assertIn('periodo', data)
        self.assertIn('total', data)
        
        # Verifica se encontrou datas
        self.assertGreater(len(data['datas']), 0)
        
        # Verifica se incluiu agendas normais e recorrentes
        datas_encontradas = data['datas']
        self.assertIn('2025-11-15', datas_encontradas)  # Agenda normal
        self.assertIn('2025-11-11', datas_encontradas)  # Agenda recorrente
        self.assertIn('2025-12-11', datas_encontradas)  # Recorrência mensal
    
    def test_agenda_page_post_datas_periodo_sucesso(self):
        """Testa endpoint POST datas-periodo com sucesso"""
        url = f'{self.agenda_page.url}datas-periodo/'
        response = self.client.post(url, {
            'start': '2025-11-01',
            'end': '2025-11-30'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('datas', data)
        self.assertGreater(len(data['datas']), 0)
    
    def test_agenda_page_datas_periodo_parametros_invalidos(self):
        """Testa endpoint com parâmetros inválidos"""
        url = f'{self.agenda_page.url}datas-periodo/'
        
        # Sem parâmetros
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
        # Data inválida
        response = self.client.get(url, {
            'start': 'data-invalida',
            'end': '2025-11-30'
        })
        self.assertEqual(response.status_code, 400)
        
        # Data final anterior à inicial
        response = self.client.get(url, {
            'start': '2025-12-01',
            'end': '2025-11-30'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_agenda_page_get_agenda_do_dia_sucesso(self):
        """Testa endpoint get_agenda_do_dia com sucesso"""
        # Testa data com agenda normal
        url = f'{self.agenda_page.url}dia/2025-11-15/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('data', data)
        self.assertIn('compromissos', data)
        self.assertEqual(data['data'], '2025-11-15')
        self.assertGreater(len(data['compromissos']), 0)
        
        # Verifica se incluiu o compromisso da agenda normal
        agenda_encontrada = False
        for compromisso in data['compromissos']:
            if compromisso['title'] == 'Reunião Teste Normal':
                agenda_encontrada = True
                break
        self.assertTrue(agenda_encontrada)
    
    def test_agenda_page_get_agenda_do_dia_recorrente(self):
        """Testa endpoint get_agenda_do_dia com data recorrente"""
        # Testa data com agenda recorrente (próximo mês da recorrência mensal)
        url = f'{self.agenda_page.url}dia/2025-12-11/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['data'], '2025-12-11')
        self.assertGreater(len(data['compromissos']), 0)
        
        # Verifica se incluiu o compromisso da agenda recorrente
        agenda_encontrada = False
        for compromisso in data['compromissos']:
            if compromisso['title'] == 'Reunião Teste Recorrente':
                agenda_encontrada = True
                break
        self.assertTrue(agenda_encontrada)
    
    def test_agenda_page_get_agenda_do_dia_data_invalida(self):
        """Testa endpoint get_agenda_do_dia com data inválida"""
        url = f'{self.agenda_page.url}dia/data-invalida/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_agenda_do_dia_page_get_datas_periodo_individual(self):
        """Testa endpoint de página individual de agenda"""
        url = f'{self.agenda_recorrente.url}datas-periodo/'
        response = self.client.get(url, {
            'start': '2025-11-01',
            'end': '2025-12-31'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verifica estrutura específica para página individual
        self.assertIn('datas', data)
        self.assertIn('agenda_id', data)
        self.assertIn('titulo', data)
        self.assertIn('tipo_recorrencia', data)
        
        # Verifica dados específicos
        self.assertEqual(data['agenda_id'], self.agenda_recorrente.id)
        self.assertEqual(data['titulo'], 'Agenda Recorrente API')
        self.assertEqual(data['tipo_recorrencia'], 'months')
        
        # Verifica se retornou apenas datas desta agenda específica (recorrência mensal)
        # Data original: 2025-11-11, próxima ocorrência: 2025-12-11
        datas_esperadas = ['2025-11-11', '2025-12-11']
        self.assertEqual(len(data['datas']), 2)
        for data_esperada in datas_esperadas:
            self.assertIn(data_esperada, data['datas'])
    
    def test_periodo_inteligente_recorrencia_diaria(self):
        """Testa expansão automática de período para recorrência diária"""
        agenda_diaria = AgendaDoDiaPage(
            title="Agenda Diária", 
            slug="agenda-diaria",
            date=date(2025, 11, 11),
            habilitar_recorrencia=True,
            tipo_recorrencia='days',
            intervalo_recorrencia=1,
            data_final_recorrencia=date(2025, 11, 15)
        )
        self.agenda_page.add_child(instance=agenda_diaria)
        agenda_diaria.save_revision().publish()
        
        # Busca com período pequeno - deve expandir automaticamente
        url = f'{self.agenda_page.url}datas-periodo/'
        response = self.client.get(url, {
            'start': '2025-11-11',
            'end': '2025-11-15'  # Apenas 5 dias
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Para recorrência diária, deve expandir para 6 meses
        # Verificar se o período foi expandido
        self.assertIn('periodo', data)
        self.assertIn('expandido_ate', data['periodo'])
        
        # Verifica se a data foi expandida além do período original
        from datetime import datetime
        fim_original = datetime.strptime('2025-11-15', '%Y-%m-%d').date()
        expandido_ate = datetime.strptime(data['periodo']['expandido_ate'], '%Y-%m-%d').date()
        self.assertGreater(expandido_ate, fim_original)
    
    def test_periodo_inteligente_recorrencia_anual(self):
        """Testa expansão automática de período para recorrência anual"""
        agenda_anual = AgendaDoDiaPage(
            title="Agenda Anual",
            slug="agenda-anual",
            date=date(2025, 11, 11),
            habilitar_recorrencia=True,
            tipo_recorrencia='years',
            intervalo_recorrencia=1,
            data_final_recorrencia=date(2027, 11, 11)
        )
        self.agenda_page.add_child(instance=agenda_anual)
        agenda_anual.save_revision().publish()
        
        # Busca com período pequeno - deve expandir para anos
        url = f'{self.agenda_page.url}datas-periodo/'
        response = self.client.get(url, {
            'start': '2025-11-11',
            'end': '2025-12-31'  # Menos de um ano
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Para recorrência anual, deve expandir para 10 anos
        self.assertIn('periodo', data)
        self.assertIn('expandido_ate', data['periodo'])
        
        # Verifica se a data foi expandida além do período original
        from datetime import datetime
        fim_original = datetime.strptime('2025-12-31', '%Y-%m-%d').date()
        expandido_ate = datetime.strptime(data['periodo']['expandido_ate'], '%Y-%m-%d').date()
        self.assertGreater(expandido_ate, fim_original)
    
    def test_resposta_json_agenda_normal_vs_recorrente(self):
        """Testa diferenças nas respostas para agendas normais vs recorrentes"""
        # Agenda normal
        url_normal = f'{self.agenda_normal.url}datas-periodo/'
        response_normal = self.client.get(url_normal, {
            'start': '2025-11-01',
            'end': '2025-11-30'
        })
        
        data_normal = json.loads(response_normal.content)
        
        # Agenda recorrente - usar período que inclui múltiplas ocorrências
        url_recorrente = f'{self.agenda_recorrente.url}datas-periodo/'
        response_recorrente = self.client.get(url_recorrente, {
            'start': '2025-11-01',
            'end': '2025-12-31'  # Expandido para incluir recorrência mensal
        })
        
        data_recorrente = json.loads(response_recorrente.content)
        
        # Agenda normal deve ter apenas uma data
        self.assertEqual(len(data_normal['datas']), 1)
        self.assertFalse(data_normal.get('tem_recorrencia', True))
        
        # Agenda recorrente deve ter múltiplas datas
        self.assertGreater(len(data_recorrente['datas']), 1)
        self.assertTrue(data_recorrente.get('tem_recorrencia', False))
    
    def test_performance_busca_periodo_grande(self):
        """Testa performance com períodos grandes"""
        url = f'{self.agenda_page.url}datas-periodo/'
        
        # Busca período de 2 anos
        start_time = datetime.now()
        response = self.client.get(url, {
            'start': '2025-01-01',
            'end': '2026-12-31'
        })
        end_time = datetime.now()
        
        # Verifica que resposta foi rápida (menos de 2 segundos)
        elapsed_time = (end_time - start_time).total_seconds()
        self.assertLess(elapsed_time, 2.0, "Busca demorou mais que 2 segundos")
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('datas', data)
    
    def test_limite_maximo_datas_retornadas(self):
        """Testa se há limite no número de datas retornadas"""
        # Cria agenda recorrente diária por período longo
        agenda_diaria_longa = AgendaDoDiaPage(
            title="Agenda Diária Longa",
            slug="agenda-diaria-longa",
            date=date(2025, 11, 11),
            habilitar_recorrencia=True,
            tipo_recorrencia='days',
            intervalo_recorrencia=1,
            data_final_recorrencia=date(2026, 11, 11)
        )
        self.agenda_page.add_child(instance=agenda_diaria_longa)
        agenda_diaria_longa.save_revision().publish()
        
        url = f'{self.agenda_page.url}datas-periodo/'
        response = self.client.get(url, {
            'start': '2025-01-01',
            'end': '2030-12-31'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verifica se há algum controle de limite
        # (ajustar conforme implementação real)
        self.assertIn('total', data)
        if 'limite_aplicado' in data:
            self.assertTrue(data['limite_aplicado'])
    
    def test_headers_resposta_api(self):
        """Testa headers da resposta da API"""
        url = f'{self.agenda_page.url}datas-periodo/'
        response = self.client.get(url, {
            'start': '2025-11-01',
            'end': '2025-11-30'
        })
        
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verifica se não há headers de cache desnecessários
        # para dados dinâmicos como agenda
        if 'Cache-Control' in response:
            self.assertIn('no-cache', response['Cache-Control'])
    
    def test_metodos_http_suportados(self):
        """Testa quais métodos HTTP são suportados"""
        url = f'{self.agenda_page.url}datas-periodo/'
        
        # GET deve funcionar
        response_get = self.client.get(url, {
            'start': '2025-11-01',
            'end': '2025-11-30'
        })
        self.assertEqual(response_get.status_code, 200)
        
        # POST deve funcionar
        response_post = self.client.post(url, {
            'start': '2025-11-01',
            'end': '2025-11-30'
        })
        self.assertEqual(response_post.status_code, 200)
        
        # PUT não deve funcionar
        response_put = self.client.put(url, {
            'start': '2025-11-01',
            'end': '2025-11-30'
        })
        self.assertEqual(response_put.status_code, 405)
        
        # DELETE não deve funcionar
        response_delete = self.client.delete(url)
        self.assertEqual(response_delete.status_code, 405)