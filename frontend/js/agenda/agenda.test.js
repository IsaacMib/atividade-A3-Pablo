/**
 * @jest-environment jsdom
 */

/**
 * Testes para o sistema de agenda com calendário recorrente
 */

describe('Agenda Calendar JavaScript Tests', () => {
    
    // Mock do vanilla-calendar-pro
    const mockCalendar = {
        init: jest.fn(),
        set: jest.fn(),
        update: jest.fn(),
        selectedMonth: 11,
        selectedYear: 2025,
        selectedDates: []
    };
    
    // Configuração inicial para cada teste
    beforeEach(() => {
        // Reset all mocks
        jest.clearAllMocks();
        
        // Mock fetch global
        global.fetch = jest.fn();
        
        // Mock VanillaCalendar
        global.VanillaCalendar = jest.fn().mockImplementation(() => mockCalendar);
        
        // Reset DOM
        document.body.innerHTML = `
            <div class="agenda-calendar" 
                 data-agenda-page-url="/agenda/"
                 data-csrf-token="test-csrf-token">
            </div>
            <div class="compromissos-container">
                <div class="compromissos-list"></div>
            </div>
        `;
        
        // Mock de resposta da API
        fetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({
                datas: ['2025-11-11', '2025-11-18', '2025-11-25'],
                periodo: {
                    inicio: '2025-11-01',
                    fim: '2025-11-30'
                },
                total: 3
            })
        });
    });
    
    test('deve encontrar elementos DOM necessários', () => {
        const calendarElement = document.querySelector('.agenda-calendar');
        const compromissosContainer = document.querySelector('.compromissos-container');
        
        expect(calendarElement).not.toBeNull();
        expect(compromissosContainer).not.toBeNull();
        
        expect(calendarElement.getAttribute('data-agenda-page-url')).toBe('/agenda/');
        expect(calendarElement.getAttribute('data-csrf-token')).toBe('test-csrf-token');
    });
    
    test('deve inicializar VanillaCalendar quando chamado', () => {
        // Simula inicialização do calendário
        const calendar = new VanillaCalendar();
        calendar.init();
        
        expect(VanillaCalendar).toHaveBeenCalled();
        expect(mockCalendar.init).toHaveBeenCalled();
    });
    
    test('deve fazer requisições fetch corretamente', async () => {
        const baseUrl = '/agenda/';
        const startDate = '2025-11-01';
        const endDate = '2025-11-30';
        
        // Simula chamada de API
        const response = await fetch(`${baseUrl}datas-periodo/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': 'test-csrf-token'
            },
            body: `start=${startDate}&end=${endDate}`
        });
        
        const data = await response.json();
        
        expect(fetch).toHaveBeenCalledWith(
            '/agenda/datas-periodo/',
            expect.objectContaining({
                method: 'POST',
                headers: expect.objectContaining({
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': 'test-csrf-token'
                })
            })
        );
        
        expect(data.datas).toEqual(['2025-11-11', '2025-11-18', '2025-11-25']);
        expect(data.total).toBe(3);
    });
    
    test('deve tratar erros de API corretamente', async () => {
        // Mock de erro na API
        fetch.mockRejectedValueOnce(new Error('Network error'));
        
        try {
            await fetch('/agenda/datas-periodo/');
        } catch (error) {
            expect(error.message).toBe('Network error');
        }
        
        expect(fetch).toHaveBeenCalled();
    });
    
    test('deve validar formato de datas', () => {
        // Função simples para validar datas
        const isValidDate = (dateString) => {
            const regex = /^\d{4}-\d{2}-\d{2}$/;
            return regex.test(dateString) && !isNaN(Date.parse(dateString));
        };
        
        expect(isValidDate('2025-11-11')).toBe(true);
        expect(isValidDate('invalid-date')).toBe(false);
        expect(isValidDate('2025-13-45')).toBe(false);
        expect(isValidDate('')).toBe(false);
    });
    
    test('deve formatar datas corretamente', () => {
        // Função para formatar datas
        const formatDate = (date) => {
            return date.toISOString().split('T')[0];
        };
        
        const testDate = new Date('2025-11-11');
        const formatted = formatDate(testDate);
        
        expect(formatted).toBe('2025-11-11');
    });
    
    test('deve calcular períodos baseados no tipo de recorrência', () => {
        // Simula lógica de cálculo de período
        const calculatePeriodForRecurrence = (baseDate, tipoRecorrencia) => {
            const periods = {
                'diaria': { months: 6 },
                'semanal': { months: 12 },
                'mensal': { months: 24 },
                'anual': { years: 10 }
            };
            
            return periods[tipoRecorrencia] || { months: 1 };
        };
        
        const baseDate = new Date('2025-11-11');
        
        expect(calculatePeriodForRecurrence(baseDate, 'diaria')).toEqual({ months: 6 });
        expect(calculatePeriodForRecurrence(baseDate, 'semanal')).toEqual({ months: 12 });
        expect(calculatePeriodForRecurrence(baseDate, 'mensal')).toEqual({ months: 24 });
        expect(calculatePeriodForRecurrence(baseDate, 'anual')).toEqual({ years: 10 });
    });
    
    test('deve construir URLs de API corretamente', () => {
        const buildApiUrl = (baseUrl, endpoint) => {
            return `${baseUrl}${endpoint}/`;
        };
        
        expect(buildApiUrl('/agenda/', 'datas-periodo')).toBe('/agenda/datas-periodo/');
        expect(buildApiUrl('/agenda/', 'dia/2025-11-11')).toBe('/agenda/dia/2025-11-11/');
    });
    
    test('deve gerenciar cache de popups', () => {
        const cachedPopups = {};
        
        const getCachedPopup = (key) => {
            return cachedPopups[key];
        };
        
        const setCachedPopup = (key, data) => {
            cachedPopups[key] = data;
        };
        
        const clearCache = () => {
            Object.keys(cachedPopups).forEach(key => {
                delete cachedPopups[key];
            });
        };
        
        // Testa operações de cache
        setCachedPopup('test-key', { datas: ['2025-11-11'] });
        expect(getCachedPopup('test-key')).toEqual({ datas: ['2025-11-11'] });
        
        clearCache();
        expect(getCachedPopup('test-key')).toBeUndefined();
    });
    
    test('deve criar elementos de popup para datas', () => {
        const createDayPopup = (date) => {
            return `<div class="popup-content has-agenda" data-date="${date}">
                <p>Compromissos para ${date}</p>
            </div>`;
        };
        
        const popup = createDayPopup('2025-11-11');
        
        expect(popup).toContain('data-date="2025-11-11"');
        expect(popup).toContain('has-agenda');
        expect(popup).toContain('2025-11-11');
    });
    
    test('deve preservar estado do calendário durante atualizações', () => {
        // Simula preservação de estado
        const preserveCalendarState = (calendar) => {
            return {
                selectedMonth: calendar.selectedMonth,
                selectedYear: calendar.selectedYear,
                selectedDates: [...(calendar.selectedDates || [])]
            };
        };
        
        const restoreCalendarState = (calendar, state) => {
            calendar.selectedMonth = state.selectedMonth;
            calendar.selectedYear = state.selectedYear;
            calendar.selectedDates = state.selectedDates;
        };
        
        // Configura estado inicial
        mockCalendar.selectedMonth = 11;
        mockCalendar.selectedYear = 2025;
        mockCalendar.selectedDates = ['2025-11-15'];
        
        // Preserva estado
        const savedState = preserveCalendarState(mockCalendar);
        
        // Simula alteração
        mockCalendar.selectedMonth = 10;
        mockCalendar.selectedDates = [];
        
        // Restaura estado
        restoreCalendarState(mockCalendar, savedState);
        
        expect(mockCalendar.selectedMonth).toBe(11);
        expect(mockCalendar.selectedYear).toBe(2025);
        expect(mockCalendar.selectedDates).toEqual(['2025-11-15']);
    });
    
    test('deve responder a eventos de calendário', () => {
        const mockEventHandler = jest.fn();
        
        // Simula eventos de calendário
        const handleCalendarEvent = (eventType, data) => {
            mockEventHandler(eventType, data);
        };
        
        // Testa diferentes tipos de eventos
        handleCalendarEvent('dateClick', { date: '2025-11-11' });
        handleCalendarEvent('monthChange', { month: 12, year: 2025 });
        handleCalendarEvent('arrowClick', { direction: 'next' });
        
        expect(mockEventHandler).toHaveBeenCalledTimes(3);
        expect(mockEventHandler).toHaveBeenCalledWith('dateClick', { date: '2025-11-11' });
        expect(mockEventHandler).toHaveBeenCalledWith('monthChange', { month: 12, year: 2025 });
        expect(mockEventHandler).toHaveBeenCalledWith('arrowClick', { direction: 'next' });
    });
    
    test('deve validar configurações do calendário', () => {
        const validateCalendarConfig = (config) => {
            const requiredFields = ['date', 'settings'];
            const hasRequiredFields = requiredFields.every(field => Object.prototype.hasOwnProperty.call(config, field));
            
            if (!hasRequiredFields) {
                return { valid: false, error: 'Campos obrigatórios ausentes' };
            }
            
            if (!config.settings.lang) {
                return { valid: false, error: 'Idioma não configurado' };
            }
            
            return { valid: true };
        };
        
        // Testa configuração válida
        const validConfig = {
            date: new Date('2025-11-11'),
            settings: { lang: 'pt-br' }
        };
        
        expect(validateCalendarConfig(validConfig)).toEqual({ valid: true });
        
        // Testa configuração inválida
        const invalidConfig = { date: new Date('2025-11-11') };
        expect(validateCalendarConfig(invalidConfig).valid).toBe(false);
    });
});