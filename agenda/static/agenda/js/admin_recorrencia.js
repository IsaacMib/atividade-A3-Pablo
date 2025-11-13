/**
 * Script para controlar a exibição dos campos de recorrência
 * no admin do Wagtail para AgendaDoDiaPage
 */
(function() {
    'use strict';

    function toggleRecorrenciaFields() {
        const habilitarRecorrencia = document.querySelector('#id_habilitar_recorrencia');
        if (!habilitarRecorrencia) {
            return;
        }

        // Busca as sections completas pelos padrões de ID do Wagtail
        const tipoSection = document.querySelector('[id*="tipo_recorrencia-section"]');
        const intervaloSection = document.querySelector('[id*="intervalo_recorrencia-section"]');
        const dataFinalSection = document.querySelector('[id*="data_final_recorrencia-section"]');

        function updateFieldsVisibility() {
            const isEnabled = habilitarRecorrencia.checked;

            // Remove/adiciona as sections completas do DOM
            if (tipoSection) {
                tipoSection.style.display = isEnabled ? '' : 'none';
            }
            
            if (intervaloSection) {
                intervaloSection.style.display = isEnabled ? '' : 'none';
            }
            
            if (dataFinalSection) {
                dataFinalSection.style.display = isEnabled ? '' : 'none';
            }
        }

        // Executa ao carregar
        updateFieldsVisibility();

        // Executa ao mudar o checkbox
        habilitarRecorrencia.addEventListener('change', updateFieldsVisibility);
    }

    // Executa quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', toggleRecorrenciaFields);
    } else {
        toggleRecorrenciaFields();
    }

    // Para Wagtail 4.0+, também escuta eventos de inicialização de formulários
    document.addEventListener('wagtail:init', function() {
        toggleRecorrenciaFields();
    });
})();
