import * as CookieConsent from "vanilla-cookieconsent";

window.CookieConsent = CookieConsent;

const CAT_NECESSARY = "necessary";
const CAT_ANALYTICS = "analytics";
const CAT_ADVERTISEMENT = "advertisement";
const CAT_FUNCTIONALITY = "functionality";
const CAT_SECURITY = "security";

const SERVICE_AD_STORAGE = 'ad_storage'
const SERVICE_AD_USER_DATA = 'ad_user_data'
const SERVICE_AD_PERSONALIZATION = 'ad_personalization'
const SERVICE_ANALYTICS_STORAGE = 'analytics_storage'
const SERVICE_FUNCTIONALITY_STORAGE = 'functionality_storage'
const SERVICE_PERSONALIZATION_STORAGE = 'personalization_storage'
const SERVICE_SECURITY_STORAGE = 'security_storage'

/**
 * Lê as configurações de cookies da meta tag
 */
function getCookieConfig() {
    const metaTag = document.querySelector('meta[name="cookie-consent-config"]');
    
    if (!metaTag) {
        return null; // Cookies não habilitados
    }
    
    const hasAnalytics = metaTag.getAttribute('data-has-analytics') === 'true';
    const analyticsTag = metaTag.getAttribute('data-analytics-tag') || '';
    
    return {
        hasAnalytics,
        analyticsTag
    };
}

/**
 * Inicializa o Cookie Consent quando a página estiver pronta
 */
function initializeCookieConsent() {
    const cookieConfig = getCookieConfig();
    
    if (!cookieConfig) {
        //console.log('Cookie Consent não habilitado - meta tag não encontrada');
        return;
    }
    
    //console.log('Inicializando Cookie Consent', cookieConfig);

    // Define dataLayer and the gtag function.
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}

    // Set default consent to 'denied' (this should happen before changing any other dataLayer)
    if (cookieConfig.hasAnalytics) {
        gtag('consent', 'default', {
            [SERVICE_AD_STORAGE]: 'denied',
            [SERVICE_AD_USER_DATA]: 'denied',
            [SERVICE_AD_PERSONALIZATION]: 'denied',
            [SERVICE_ANALYTICS_STORAGE]: 'denied',
            [SERVICE_FUNCTIONALITY_STORAGE]: 'denied',
            [SERVICE_PERSONALIZATION_STORAGE]: 'denied',
            [SERVICE_SECURITY_STORAGE]: 'denied',
        });
    }

    /** 
     * Update gtag consent according to the users choices made in CookieConsent UI
     */
    function updateGtagConsent() {
        if (cookieConfig.hasAnalytics) {
            gtag('consent', 'update', {
                [SERVICE_ANALYTICS_STORAGE]: CookieConsent.acceptedService(SERVICE_ANALYTICS_STORAGE, CAT_ANALYTICS) ? 'granted' : 'denied',
                [SERVICE_AD_STORAGE]: CookieConsent.acceptedService(SERVICE_AD_STORAGE, CAT_ADVERTISEMENT) ? 'granted' : 'denied',
                [SERVICE_AD_USER_DATA]: CookieConsent.acceptedService(SERVICE_AD_USER_DATA, CAT_ADVERTISEMENT) ? 'granted' : 'denied',
                [SERVICE_AD_PERSONALIZATION]: CookieConsent.acceptedService(SERVICE_AD_PERSONALIZATION, CAT_ADVERTISEMENT) ? 'granted' : 'denied',
                [SERVICE_FUNCTIONALITY_STORAGE]: CookieConsent.acceptedService(SERVICE_FUNCTIONALITY_STORAGE, CAT_FUNCTIONALITY) ? 'granted' : 'denied',
                [SERVICE_PERSONALIZATION_STORAGE]: CookieConsent.acceptedService(SERVICE_PERSONALIZATION_STORAGE, CAT_FUNCTIONALITY) ? 'granted' : 'denied',
                [SERVICE_SECURITY_STORAGE]: CookieConsent.acceptedService(SERVICE_SECURITY_STORAGE, CAT_SECURITY) ? 'granted' : 'denied',
            });
        }
    }

    // Executa o CookieConsent
    CookieConsent.run({
    // See: https://cookieconsent.orestbida.com/reference/configuration-reference.html#guioptions
    // ...
    guiOptions: {
        consentModal: {
            layout: "bar inline",
            position: "bottom",
            equalWeightButtons: true,
            flipButtons: false
        },
        preferencesModal: {
            layout: "box",
            position: "right",
            equalWeightButtons: true,
            flipButtons: false
        }
    },
    
    // Trigger consent update when user choices change
    onFirstConsent: () => {
        updateGtagConsent();
    },
    onConsent: () => {
        updateGtagConsent();
    },
    onChange: () => {
        updateGtagConsent();
    },

    // Configure categories and services
    categories: {
        [CAT_NECESSARY]: {
            enabled: true,  // this category is enabled by default
            readOnly: true,  // this category cannot be disabled
        },
        [CAT_ANALYTICS]: {
            enabled: true,  // this category is enabled by default
            autoClear: {
                cookies: [
                    {
                        name: /^_ga/,   // regex: match all cookies starting with '_ga'
                    },
                    {
                        name: '_gid',   // string: exact cookie name
                    }
                ]
            },
            // See: https://cookieconsent.orestbida.com/reference/configuration-reference.html#category-services
            services: {
                [SERVICE_ANALYTICS_STORAGE]: {
                    label: 'Permite armazenamento (como cookies) relacionado à análise, por exemplo, duração da visita.',
                }
            }
        },
        [CAT_ADVERTISEMENT]: {
            services: {
                [SERVICE_AD_STORAGE]: {
                    label: 'Permite armazenamento (como cookies) relacionado à publicidade.',
                },
                [SERVICE_AD_USER_DATA]: {
                    label: 'Define consentimento para envio de dados do usuário relacionados à publicidade para o Google.',
                },
                [SERVICE_AD_PERSONALIZATION]: {
                    label: 'Define consentimento para publicidade personalizada.',
                },
            }
        },
        [CAT_FUNCTIONALITY]: {
            services: {
                [SERVICE_FUNCTIONALITY_STORAGE]: {
                    label: 'Permite armazenamento que suporte a funcionalidade do site ou aplicativo, por exemplo, configurações de idioma.',
                },
                [SERVICE_PERSONALIZATION_STORAGE]: {
                    label: 'Permite armazenamento relacionado à personalização, por exemplo, recomendações de vídeo.',
                },
            }
        },
        [CAT_SECURITY]: {
            services: {
                [SERVICE_SECURITY_STORAGE]: {
                    label: 'Permite armazenamento relacionado à segurança, como funcionalidade de autenticação, prevenção de fraudes e outras proteções do usuário.',
                },
            }
        }
    },

    language: {
        default: 'ptbr',
        translations: {
            ptbr: {
                // See: https://support.google.com/tagmanager/answer/10718549?hl=en
                consentModal: {
                    title: 'Nós usamos cookies',
                    description: 'Este site usa cookies essenciais para garantir seu funcionamento adequado e cookies de rastreamento para entender como você interage com ele. Os últimos serão definidos apenas após o consentimento.',
                    acceptAllBtn: 'Aceitar todos',
                    acceptNecessaryBtn: 'Rejeitar todos',
                    showPreferencesBtn: 'Gerenciar preferências individuais'
                },
                preferencesModal: {
                    title: 'Gerenciar preferências de cookies',
                    acceptAllBtn: 'Aceitar todos',
                    acceptNecessaryBtn: 'Rejeitar todos',
                    savePreferencesBtn: 'Aceitar seleção atual',
                    closeIconLabel: 'Fechar modal',
                    sections: [
                        {
                            title: "Uso de cookies",
                            description: "Usamos cookies para garantir as funcionalidades básicas do site e para melhorar sua experiência online."
                        },
                        {
                            title: "Cookies estritamente necessários",
                            description: "Estes cookies são essenciais para o funcionamento adequado do site, por exemplo, para autenticação do usuário.",
                            linkedCategory: CAT_NECESSARY,
                        },
                        {
                            title: "Análise",
                            description: 'Cookies usados para análise ajudam a coletar dados que permitem aos serviços entender como os usuários interagem com um serviço específico. Essas informações permitem que os serviços melhorem o conteúdo e construam melhores recursos que aprimoram a experiência do usuário.',
                            linkedCategory: CAT_ANALYTICS,
                            cookieTable: {
                                headers: {
                                    name: "Nome",
                                    domain: "Serviço",
                                    description: "Descrição",
                                    expiration: "Expiração"
                                },
                                body: [
                                    {
                                        name: "_ga",
                                        domain: "Google Analytics",
                                        description: "Cookie definido pelo <a href=\"https://business.safety.google/adscookies/\">Google Analytics</a>",
                                        expiration: "Expira após 12 dias"
                                    },
                                    {
                                        name: "_gid",
                                        domain: "Google Analytics",
                                        description: "Cookie definido pelo <a href=\"https://business.safety.google/adscookies/\">Google Analytics</a>",
                                        expiration: "Sessão"
                                    }
                                ]
                            }
                        },
                        // {
                        //     title: 'Advertising',
                        //     description: 'Google uses cookies for advertising, including serving and rendering ads, personalizing ads (depending on your ad settings at <a href=\"https://g.co/adsettings\">g.co/adsettings</a>), limiting the number of times an ad is shown to a user, muting ads you have chosen to stop seeing, and measuring the effectiveness of ads.',
                        //     linkedCategory: CAT_ADVERTISEMENT,
                        // },
                        // {
                        //     title: 'Functionality',
                        //     description: 'Cookies used for functionality allow users to interact with a service or site to access features that are fundamental to that service. Things considered fundamental to the service include preferences like the user's choice of language, product optimizations that help maintain and improve a service, and maintaining information relating to a user's session, such as the content of a shopping cart.',
                        //     linkedCategory: CAT_FUNCTIONALITY,
                        // },
                        // {
                        //     title: 'Security',
                        //     description: 'Cookies used for security authenticate users, prevent fraud, and protect users as they interact with a service.',
                        //     linkedCategory: CAT_SECURITY,
                        // },
                        {
                            title: 'Mais informações',
                            description: 'Para qualquer dúvida em relação à política de cookies e suas escolhas, por favor <a href="https://www.example.com/contacts">entre em contato conosco</a>.'
                        }
                    ]
                }
            },
            en: {
                // See: https://support.google.com/tagmanager/answer/10718549?hl=en
                consentModal: {
                    title: 'We use cookies',
                    description: 'This website uses essential cookies to ensure its proper operation and tracking cookies to understand how you interact with it. The latter will be set only after consent.',
                    acceptAllBtn: 'Accept all',
                    acceptNecessaryBtn: 'Reject all',
                    showPreferencesBtn: 'Manage Individual preferences'
                },
                preferencesModal: {
                    title: 'Manage cookie preferences',
                    acceptAllBtn: 'Accept all',
                    acceptNecessaryBtn: 'Reject all',
                    savePreferencesBtn: 'Accept current selection',
                    closeIconLabel: 'Close modal',
                    sections: [
                        {
                            title: "Cookie usage",
                            description: "We use cookies to ensure the basic functionalities of the website and to enhance your online experience."
                        },
                        {
                            title: "Strictly necessary cookies",
                            description: "These cookies are essential for the proper functioning of the website, for example for user authentication.",
                            linkedCategory: CAT_NECESSARY,
                        },
                        {
                            title: "Analytics",
                            description: 'Cookies used for analytics help collect data that allows services to understand how users interact with a particular service. These insights allow services both to improve content and to build better features that improve the user’s experience.',
                            linkedCategory: CAT_ANALYTICS,
                            cookieTable: {
                                headers: {
                                    name: "Name",
                                    domain: "Service",
                                    description: "Description",
                                    expiration: "Expiration"
                                },
                                body: [
                                    {
                                        name: "_ga",
                                        domain: "Google Analytics",
                                        description: "Cookie set by <a href=\"https://business.safety.google/adscookies/\">Google Analytics</a>",
                                        expiration: "Expires after 12 days"
                                    },
                                    {
                                        name: "_gid",
                                        domain: "Google Analytics",
                                        description: "Cookie set by <a href=\"https://business.safety.google/adscookies/\">Google Analytics</a>",
                                        expiration: "Session"
                                    }
                                ]
                            }
                        },
                        // {
                        //     title: 'Advertising',
                        //     description: 'Google uses cookies for advertising, including serving and rendering ads, personalizing ads (depending on your ad settings at <a href=\"https://g.co/adsettings\">g.co/adsettings</a>), limiting the number of times an ad is shown to a user, muting ads you have chosen to stop seeing, and measuring the effectiveness of ads.',
                        //     linkedCategory: CAT_ADVERTISEMENT,
                        // },
                        // {
                        //     title: 'Functionality',
                        //     description: 'Cookies used for functionality allow users to interact with a service or site to access features that are fundamental to that service. Things considered fundamental to the service include preferences like the user’s choice of language, product optimizations that help maintain and improve a service, and maintaining information relating to a user’s session, such as the content of a shopping cart.',
                        //     linkedCategory: CAT_FUNCTIONALITY,
                        // },
                        // {
                        //     title: 'Security',
                        //     description: 'Cookies used for security authenticate users, prevent fraud, and protect users as they interact with a service.',
                        //     linkedCategory: CAT_SECURITY,
                        // },
                        {
                            title: 'More information',
                            description: 'For any queries in relation to the policy on cookies and your choices, please <a href="https://www.example.com/contacts">contact us</a>.'
                        }
                    ]
                }
            }
        }
      }
    });
}

// Aguarda o DOM estar pronto antes de inicializar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCookieConsent);
} else {
    initializeCookieConsent();
}