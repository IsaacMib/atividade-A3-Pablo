document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.querySelector('.site-menu-navbar-toggler');
    
    // Função para calcular e definir a posição top do navbar collapse
    function calculateNavbarPosition() {
        const mobileNavbar = document.querySelector('.site-menu-navbar-mobile');
        const navbarCollapse = document.querySelector('.site-menu-navbar-collapse');
        // const barraBrasil = document.getElementById('barra-brasil'); // Comentado temporariamente

        console.info('Calculando posição do navbar collapse');
        
        if (mobileNavbar && navbarCollapse) {
            const mobileRect = mobileNavbar.getBoundingClientRect();
            let topPosition = mobileRect.height;

            console.info('Altura do navbar mobile:', mobileRect.height);
            
            // Adiciona a altura da barra-brasil se ela existir
            // if (barraBrasil) {
            //     const barraRect = barraBrasil.getBoundingClientRect();
            //     topPosition += barraRect.height;
            // }
            
            navbarCollapse.style.top = `${topPosition}px`;
            console.info('navbarCollapse.style.top:', navbarCollapse.style.top);
        }
    }
    
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            console.log('click');
            
            // Verifica se o menu está sendo aberto ou fechado
            const isExpanded = toggleButton.getAttribute('aria-expanded') === 'true';

            // Calcula a posição usando a função
            calculateNavbarPosition();
            
            if (isExpanded) {
              // Menu está sendo aberto
              
              // Cria o backdrop
              const backdrop = document.createElement('div');
              backdrop.className = 'modal-backdrop-trigger';
              backdrop.style.cssText = `
                  position: fixed;
                  top: 0;
                  left: 0;
                  width: 100%;
                  height: 100%;
                  background-color: rgba(0, 0, 0, 0.5);
                  z-index: 2;
              `;
              document.body.appendChild(backdrop);
              
              // Fechar menu ao clicar no backdrop
              backdrop.addEventListener('click', function() {
                  toggleButton.click();
              });
                
            } else {
              setTimeout(() => {
                // Menu está sendo fechado, remove o backdrop
                const backdrop = document.querySelector('.modal-backdrop-trigger');
                if (backdrop) {
                    backdrop.remove();
                }  
              }, 150);
            }
        });
    }

    // Listener para resize da tela
    window.addEventListener('resize', function() {
        const toggleButton = document.querySelector('.site-menu-navbar-toggler');
        const isExpanded = toggleButton ? toggleButton.getAttribute('aria-expanded') === 'true' : false;
        
        if (window.innerWidth > 992) {
            const backdrop = document.querySelector('.modal-backdrop-trigger');
            if (backdrop) {
                backdrop.remove();
            }
        } else if (window.innerWidth <= 992 && isExpanded) {
            // Se a tela for menor que 992px e o menu estiver expandido, adiciona o backdrop
            const existingBackdrop = document.querySelector('.modal-backdrop-trigger');
            if (!existingBackdrop) {
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop-trigger';
                backdrop.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    z-index: 5;
                `;
                document.body.appendChild(backdrop);
                
                // Fechar menu ao clicar no backdrop
                backdrop.addEventListener('click', function() {
                    toggleButton.click();
                });
            }
        }
    });
});