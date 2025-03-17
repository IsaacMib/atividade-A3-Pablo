import "../scss/main.scss";
import "../../tw/styles.css";

import bootstrap from 'bootstrap';

import BarraIdentidade from './barraidentidadepb/barraidentidadepb.js';

window.barraIdentidade = new BarraIdentidade;

document.addEventListener("DOMContentLoaded", function() {
  window.addEventListener("resize", function() {
    window.barraIdentidade.checkScrollBarra(document.getElementById("menu-barra-brasil"));
  });
  document.addEventListener("mouseup", function(e) {
    var container = document.getElementById("barra-brasil");
    // if the target of the click isn't the container nor a descendant of the container
    if (!container.contains(e.target)) {
      window.barraIdentidade.closeAllToggleGoverno();
    }
  });
});