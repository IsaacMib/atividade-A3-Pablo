function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  applyTheme(newTheme);
  document.getElementById('theme-toggle').textContent = newTheme === 'dark' ? '☀️ Alternar Tema' : '🌙 Alternar Tema';
}

// Aplica o tema salvo no localStorage ao carregar a página
document.addEventListener("DOMContentLoaded", function () {
  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);
  document.getElementById('theme-toggle').textContent = savedTheme === 'dark' ? '☀️ Alternar Tema' : '🌙 Alternar Tema';
});

// Adiciona o evento de clique à tag <a>
document.getElementById('theme-toggle').addEventListener('click', function (event) {
  event.preventDefault(); // Evita que o link recarregue a página
  toggleTheme();
});