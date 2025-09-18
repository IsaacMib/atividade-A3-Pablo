function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  document.documentElement.setAttribute('data-bs-theme', theme);
  if (theme === 'light') {
    document.documentElement.classList.remove('cc--darkmode');
    // document.documentElement.classList.remove('cc--elegant-black');
    document.documentElement.classList.add('cc--light-funky');
  } else if (theme === 'dark') {
    document.documentElement.classList.add('cc--darkmode');
    // document.documentElement.classList.add('cc--elegant-black');
    document.documentElement.classList.remove('cc--light-funky');
  }
  localStorage.setItem('theme', theme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  applyTheme(newTheme);
  //document.getElementById('theme-toggle').textContent = newTheme === 'dark' ? '☀️ Alternar Tema' : '🌙 Alternar Tema';
}

// Aplica o tema salvo no localStorage ao carregar a página
document.addEventListener("DOMContentLoaded", function () {
  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);
  //document.getElementById('theme-toggle').textContent = savedTheme === 'dark' ? '☀️ Alternar Tema' : '🌙 Alternar Tema';
});

// Adiciona o evento de clique à tag <a>
document.getElementById('theme-toggle').addEventListener('click', function (event) {
  event.preventDefault(); // Evita que o link recarregue a página
  toggleTheme();
});

document.getElementById('theme-toggle-mobile').addEventListener('click', function (event) {
  event.preventDefault(); // Evita que o link recarregue a página
  toggleTheme();
});

document.addEventListener('DOMContentLoaded', function () {
  // Fecha accordions internos quando o dropdown principal é fechado
  document.querySelectorAll('.site-menu-dropdown-item.dropdown').forEach(function (dropdown) {
    dropdown.addEventListener('hide.bs.site-menu-dropdown-item.dropdown', function () {
      dropdown.querySelectorAll('.site-menu-accordion-collapse.accordion-collapse.show').forEach(function (acc) {
        // Dispara o click no botão do accordion aberto para fechar corretamente
        var btn = acc.closest('.site-menu-accordion-item.accordion-item').querySelector('.site-menu-accordion-button.accordion-button');
        if (btn && !btn.classList.contains('collapsed')) {
          btn.click();
        }
      });
    });
  });

  // Previne que o dropdown principal seja fechado ao clicar no accordion do nível 2
  document.querySelectorAll('.site-menu-accordion-button.accordion-button').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
    });
  });
});