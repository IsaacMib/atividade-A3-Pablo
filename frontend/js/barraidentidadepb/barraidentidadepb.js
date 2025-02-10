export default class BarraIdentidade {
    closeAllToggleGoverno() {
        var a, r, i, o, e;
        var elementID = "servicos-governo-barra";
        o = document.getElementById(elementID)
        if(o != null && typeof a != null && typeof o != null && typeof o != undefined){
            if (o = document.getElementById(elementID),
            i = document.getElementById("link-servicos"),
            a = document.getElementsByClassName("link-externo-barra"),
            e = o.classList.contains("mostra-orgaos")) {
                for (o.classList.remove("mostra-orgaos"),
                r = 0; r < a.length; )
                    a[r].classList.remove("link-discreto-fixo"),
                    r++;
                i.classList.remove("link-cima-barra");
                i.classList.remove("ativo");
                i.classList.remove("close");
            }

            i.classList.remove("close");
        }
        
        elementID = "indiretas-governo-barra";
        o = document.getElementById(elementID)
        if(o != null && typeof a != null && typeof o != null && typeof o != undefined){
            if (o = document.getElementById(elementID),
            i = document.getElementById("link-indiretas"),
            a = document.getElementsByClassName("link-externo-barra"),
            e = o.classList.contains("mostra-orgaos")) {
                for (o.classList.remove("mostra-orgaos"),
                r = 0; r < a.length; )
                    a[r].classList.remove("link-discreto-fixo"),
                    r++;
                i.classList.remove("link-cima-barra");
                i.classList.remove("ativo");
                i.classList.remove("close");
            }

            i.classList.remove("close");
        }
    }

    closeServicoToggleGoverno() {
        var a, r, i, o, e;
        var elementID = "servicos-governo-barra";
        o = document.getElementById(elementID)
        if(o != null && typeof a != null && typeof o != null && typeof o != undefined){
            if (o = document.getElementById(elementID),
            i = document.getElementById("link-servicos"),
            a = document.getElementsByClassName("link-externo-barra"),
            e = o.classList.contains("mostra-orgaos")) {
                for (o.classList.remove("mostra-orgaos"),
                r = 0; r < a.length; )
                    a[r].classList.remove("link-discreto-fixo"),
                    r++;
                i.classList.remove("link-cima-barra");
                i.classList.remove("ativo")
            }
        }
    }

    closeIndiretasToggleGoverno() {
        var a, r, i, o, e;
        var elementID = "indiretas-governo-barra";
        o = document.getElementById(elementID)
        if(o != null && typeof a != null && typeof o != null && typeof o != undefined){
            if (o = document.getElementById(elementID),
            i = document.getElementById("link-indiretas"),
            a = document.getElementsByClassName("link-externo-barra"),
            e = o.classList.contains("mostra-orgaos")) {
                for (o.classList.remove("mostra-orgaos"),
                r = 0; r < a.length; )
                    a[r].classList.remove("link-discreto-fixo"),
                    r++;
                i.classList.remove("link-cima-barra");
                i.classList.remove("ativo")
            }
        }
    }

    toggleOrgaosGoverno() {
        var a, r, i, o, e;
        var elementID = "orgaos-governo-barra";
        o = document.getElementById(elementID)
        if(o != null && typeof a != null && typeof o != null && typeof o != undefined){
            if (o = document.getElementById(elementID),
            i = document.getElementById("link-orgaos"),
            a = document.getElementsByClassName("link-externo-barra"),
            e = o.classList.contains("mostra-orgaos")) {
                for (o.classList.remove("mostra-orgaos"),
                r = 0; r < a.length; )
                    a[r].classList.remove("link-discreto-fixo"),
                    r++;
                setTimeout(i.classList.remove("link-cima-barra"), 500)
            } else {
                for (r = 0; r < a.length; )
                    a[r].classList.add("link-discreto-fixo"),
                    r++;
                o.classList.add("mostra-orgaos"),
                i.classList.add("link-cima-barra")
            }
        }
    }

    toggleServicosGoverno() {
        this.closeIndiretasToggleGoverno()
        var a, r, i, o, e;
        var elementID = "servicos-governo-barra";
        o = document.getElementById(elementID)
        if(o != null && typeof a != null && typeof o != null && typeof o != undefined){
            if (o = document.getElementById(elementID),
            i = document.getElementById("link-servicos"),
            a = document.getElementsByClassName("link-externo-barra"),
            e = o.classList.contains("mostra-orgaos")) {
                for (o.classList.remove("mostra-orgaos"),
                r = 0; r < a.length; )
                    a[r].classList.remove("link-discreto-fixo"),
                    r++;
                i.classList.remove("link-cima-barra");
                i.classList.remove("close")
                i = document.getElementById("link-indiretas")
                i.classList.remove("close")
            } else {
                for (r = 0; r < a.length; )
                    a[r].classList.add("link-discreto-fixo"),
                    r++;
                o.classList.add("mostra-orgaos"),
                i.classList.add("link-cima-barra")
                i.classList.add("ativo")
                
                i.classList.remove("close")
                i = document.getElementById("link-indiretas")
                i.classList.add("close")
            }
        }
    }

    toggleIndiretasGoverno() {
        this.closeServicoToggleGoverno();
        var a, r, i, o, e;
        var elementID = "indiretas-governo-barra";
        o = document.getElementById(elementID)
        if(o != null && typeof a != null && typeof o != null && typeof o != undefined){
            if (o = document.getElementById(elementID),
            i = document.getElementById("link-indiretas"),
            a = document.getElementsByClassName("link-externo-barra"),
            e = o.classList.contains("mostra-orgaos")) {
                for (o.classList.remove("mostra-orgaos"),
                r = 0; r < a.length; )
                    a[r].classList.remove("link-discreto-fixo"),
                    r++;
                i.classList.remove("link-cima-barra");
                i.classList.remove("close")
                i = document.getElementById("link-servicos")
                i.classList.remove("close")
            } else {
                for (r = 0; r < a.length; )
                    a[r].classList.add("link-discreto-fixo"),
                    r++;
                o.classList.add("mostra-orgaos"),
                i.classList.add("link-cima-barra")
                i.classList.add("ativo")
                
                i.classList.remove("close")
                i = document.getElementById("link-servicos")
                i.classList.add("close")
            }
        }
    }

    scrollBarra() {
        var a, r, i;
        r = 0,
        a = document.getElementById("menu-barra-brasil"),
        i = setInterval(function() {
            return a.scrollLeft += 20,
            r += 20,
            r >= 100 ? window.clearInterval(i) : void 0
        }, 100);
    }

    scrollBarraEsquerda() {
        var a, r, i;
        r = 100,
        a = document.getElementById("menu-barra-brasil"),
        i = setInterval(function() {
            var newScroll = a.scrollLeft - 20
            if (newScroll <= 0) {
                newScroll = 0
            }
            return a.scrollLeft = newScroll,
            r -= 20,
            r <= 0 ? window.clearInterval(i) : void 0
        }, 100);
    }

    checkScrollBarra(a) {
        if (a.scrollLeft <= 0) {
            document.getElementById("botao-seta-direita").style.display = "block"
            document.getElementById("botao-seta-esquerda").style.display = "none"
        } else if (a.scrollLeft > 0 && a.scrollLeft < a.scrollWidth - a.clientWidth -20) {
            document.getElementById("botao-seta-direita").style.display = "block"
            document.getElementById("botao-seta-esquerda").style.display = "block"
        } else {
            document.getElementById("botao-seta-direita").style.display = "none"
            document.getElementById("botao-seta-esquerda").style.display = "block"
        }
    }
}