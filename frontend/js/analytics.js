/**
 * Google Analytics (gtag.js)
 * 
 * Carregado condicionalmente se google_analytics_tag está configurado
 * em SiteSettings (tem_google_analytics = True)
 */

// Inicializar dataLayer
window.dataLayer = window.dataLayer || [];

function gtag() {
  dataLayer.push(arguments);
}

// Configurar gtag
gtag('js', new Date());

// Tag será injetada via data-attribute no script
const analyticsTag = document.currentScript?.dataset.analyticsTag;
if (analyticsTag) {
  gtag('config', analyticsTag);
}
