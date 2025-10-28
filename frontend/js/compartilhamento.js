/**
 * Funcionalidades do sistema de compartilhamento de conteúdos
 */
class CompartilhamentoSocial {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupCopyButtons();
            this.setupSocialButtons();
        });
    }

    setupCopyButtons() {
        const copyButtons = document.querySelectorAll('.btn-copy-link');
        
        // Inicializa popovers do Bootstrap
        copyButtons.forEach(button => {
            // Cria uma instância do popover Bootstrap
            const popover = new window.bootstrap.Popover(button, {
                placement: 'top',
                content: 'Link copiado com sucesso!',
                trigger: 'manual',
                title: '', // Explicitamente sem título
                customClass: 'copy-success-popover'
            });
            
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const url = button.getAttribute('data-url');
                
                // Tenta usar a API moderna do clipboard
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(url)
                        .then(() => this.showCopyPopover(popover))
                        .catch(() => this.fallbackCopyTextToClipboard(url, popover));
                } else {
                    // Fallback para navegadores mais antigos
                    this.fallbackCopyTextToClipboard(url, popover);
                }
            });
        });
    }

    setupSocialButtons() {
        const socialButtons = document.querySelectorAll('.btn-compartilhar:not(.btn-copy-link)');
        
        socialButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const url = button.getAttribute('href');
                const rede = button.getAttribute('data-rede');
                
                // Configurações específicas para cada rede social
                const popupConfig = this.getPopupConfig(rede);
                
                // Abre o pop-up
                this.openPopup(url, rede, popupConfig);
            });
        });
    }

    getPopupConfig(rede) {
        const configs = {
            facebook: {
                width: 626,
                height: 436,
                title: 'Compartilhar no Facebook'
            },
            twitter: {
                width: 626,
                height: 436,
                title: 'Compartilhar no X (Twitter)'
            },
            linkedin: {
                width: 626,
                height: 450,
                title: 'Compartilhar no LinkedIn'
            },
            whatsapp: {
                width: 626,
                height: 450,
                title: 'Compartilhar no WhatsApp'
            },
            telegram: {
                width: 626,
                height: 450,
                title: 'Compartilhar no Telegram'
            },
            email: {
                width: 800,
                height: 600,
                title: 'Compartilhar por E-mail'
            }
        };

        return configs[rede] || {
            width: 626,
            height: 450,
            title: 'Compartilhar'
        };
    }

    openPopup(url, rede, config) {
        // Calcula a posição centralizada
        const left = (window.screen.width / 2) - (config.width / 2);
        const top = (window.screen.height / 2) - (config.height / 2);
        
        // Configurações da janela pop-up
        const features = [
            `width=${config.width}`,
            `height=${config.height}`,
            `left=${left}`,
            `top=${top}`,
            'menubar=no',
            'toolbar=no',
            'status=no',
            'scrollbars=yes',
            'resizable=yes'
        ].join(',');
        
        // Abre a janela pop-up
        const popup = window.open(url, `compartilhar_${rede}`, features);
        
        // Foca na janela pop-up se ela foi criada com sucesso
        if (popup) {
            popup.focus();
        } else {
            // Fallback: se o pop-up foi bloqueado, abre em nova aba
            console.warn('Pop-up bloqueado, abrindo em nova aba...');
            window.open(url, '_blank', 'noopener,noreferrer');
        }
    }

    fallbackCopyTextToClipboard(text, popover) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showCopyPopover(popover);
        } catch (err) {
            console.error('Erro ao copiar link: ', err);
        }
        
        document.body.removeChild(textArea);
    }

    showCopyPopover(popover) {
        if (popover) {
            // Mostra o popover
            popover.show();
            
            // Esconde automaticamente após 2 segundos
            setTimeout(() => {
                popover.hide();
            }, 2000);
        }
    }
}

// Inicializa o sistema de compartilhamento
new CompartilhamentoSocial();