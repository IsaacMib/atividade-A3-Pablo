import "../scss/main.scss";
import "../../tw/styles.css";

import * as bootstrap from 'bootstrap';
window.bootstrap = bootstrap;

import BarraIdentidade from './barraidentidadepb/barraidentidadepb.js';

import UIkit from 'uikit';
import Icons from 'uikit/dist/js/uikit-icons';

import './header/header.js';

import Swiper from 'swiper/bundle';

import 'swiper/css/bundle';

// loads the Icon plugin
UIkit.use(Icons);

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

const swiper = new Swiper(".swiperServicosOnline", {
  slidesPerView: 1,
  spaceBetween: 2,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  breakpoints: {
    640: {
      slidesPerView: 1,
      spaceBetween: 20,
    },
    768: {
      slidesPerView: 2,
      spaceBetween: 40,
    },
    1024: {
      slidesPerView: 3,
      spaceBetween: 50,
    },
  },
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
});