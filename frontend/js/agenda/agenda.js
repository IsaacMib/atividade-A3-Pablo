document.addEventListener("DOMContentLoaded", function() {
    const compromissosList = document.getElementById("compromissos-list");
    if (!compromissosList) {
        return;
    }
    const baseUrl = window.location.origin + "/agendas";
    const pageSlug = compromissosList.getAttribute("data-page-slug");
    const { Calendar } = window.VanillaCalendarPro;

    // Obtém as datas do atributo data-datas-agenda
    const calendarAgendas = document.getElementById("calendar-agendas");
    let datasAgenda = [];
    if (calendarAgendas) {
        try {
            datasAgenda = JSON.parse(calendarAgendas.getAttribute("data-datas-agenda").replace(/'/g, '"'));
        } catch (e) {
            datasAgenda = [];
        }
    }

    // Monta o objeto popups a partir das datas
    const popups = {};
    datasAgenda.forEach(data => {
        popups[data] = {
            modifier: 'bg-temcompromissos',
            html: '',
        };
    });

    const options = {
        locale: 'pt-BR',
        type: 'multiple',
        selectedTheme: 'light',
        displayMonthsCount: 2,
        monthsToSwitch: 1,
        selectionDatesMode: 'single',
        firstWeekday: 1,
        disableAllDates: false,
        popups: popups,
        onClickDate(self) {
        //   console.log("Mês selecionado:", self.context.selectedMonth);
        //   console.log("Ano selecionado:", self.context.selectedYear);
        //   console.log("Data selecionada:", self.context.selectedDates);
          const selectedDate = self.context.selectedDates[0];
          if (selectedDate) {
              loadCompromissos(selectedDate);

              // Atualiza a URL
              const url = new URL(window.location);
              url.searchParams.set('data', selectedDate);
              window.history.pushState({}, '', url);
          }
        },
        // onClickMonth(self) {
        //   console.log("Mês selecionado:", self.context.selectedMonth);
        //   console.log("Ano selecionado:", self.context.selectedYear);
        //   console.log("Data selecionada:", self.context.selectedDates);
        // },
        // onClickYear(self) {
        //   console.log("Mês selecionado:", self.context.selectedMonth);
        //   console.log("Ano selecionado:", self.context.selectedYear);
        //   console.log("Data selecionada:", self.context.selectedDates);
        // },
    };
    
    const calendar = new Calendar('#calendar-agendas', options);
    
    const layoutMultiple = `
        <div class="calendar-arrow-lg calendar-arrow-prev" role="toolbar" aria-label="${calendar.labels.navigation}">
            <#ArrowPrev [month] />
        </div>
        <div class="${calendar.styles.grid}" data-vc="grid">
            <#Multiple>
            <div class="${calendar.styles.column}" data-vc="column" role="region">
                <div class="${calendar.styles.header}" data-vc="header">
                    <div class="${calendar.styles.headerContent}" data-vc-header="content">
                        <div class="calendar-arrow-sm">
                            <#ArrowPrev [month] />
                        </div>
                        <#Month />
                        <#Year />
                        <div class="calendar-arrow-sm">
                        <#ArrowNext [month] />
                        </div>
                    </div>
                </div>
                <div class="${calendar.styles.wrapper}" data-vc="wrapper">
                    <#WeekNumbers />
                    <div class="${calendar.styles.content}" data-vc="content">
                        <#Week />
                        <#Dates />
                    </div>
                </div>
            </div>
            <#/Multiple>
            <#DateRangeTooltip />
        </div>
        <div class="calendar-arrow-lg calendar-arrow-next" role="toolbar" aria-label="${calendar.labels.navigation}">
            <#ArrowNext [month] />
        </div>
        <#ControlTime />
        `;

      calendar.layouts.multiple = layoutMultiple;
    
    
    function formatHoraMinuto(horario) {
        if (!horario) return "";
        const partes = horario.split(":");
        if (partes.length >= 2) {
            return `${partes[0]}:${partes[1]}`;
        }
        return horario;
    }

    // Função para carregar compromissos de uma data específica
    function loadCompromissos(selectedDate) {
        const compromissoTitle = document.getElementById("compromissos-title")
        if (selectedDate) {
            fetch(`${baseUrl}/${pageSlug}/dia/${selectedDate}/`)
                .then(response => response.json())
                .then(data => {
                    compromissosList.innerHTML = ""; // Limpa a lista
                    const container = document.createElement("div");
                    container.className = "row justify-content-center align-items-center"; // Bootstrap row

                    if (data.compromissos && data.compromissos.length > 0) {
                        compromissoTitle.classList.remove("no-compromissos");
                        //compromissoTitle.innerHTML = "Compromissos";
                        data.compromissos.forEach(compromisso => {
                            const col = document.createElement("div");
                            col.className = "agenda-item-col col-md-6 col-lg-auto mb-4"; // 4 colunas por linha

                            col.innerHTML = `
                                <div class="agenda-item">
                                    <div class="agenda-item--title">${compromisso.title || ""}</div>
                                    <div class="agenda-item--divider"></div>
                                    <div class="agenda-item--descricao">${compromisso.pauta || ""}</div>
                                    <div class="agenda-item--horario-local">
                                      <div class="agenda-item--local">
                                        <i class="agenda-item--icon fa-solid fa-location-dot"></i>
                                        <span>${compromisso.local || ""}</span>
                                      </div>
                                      <div class="agenda-item--horario">
                                        <i class="agenda-item--icon fa-solid fa-clock"></i>
                                        <span>${
                                          compromisso.inicio === compromisso.termino
                                            ? formatHoraMinuto(compromisso.inicio)
                                            : `${formatHoraMinuto(compromisso.inicio)} - ${formatHoraMinuto(compromisso.termino)}`
                                        }</span>
                                      </div>
                                    </div>
                                </div>
                            `;
                            container.appendChild(col);
                        });
                    } else {
                        //compromissoTitle.innerHTML = "<div></div>"; // Limpa o título se não houver compromissos
                        compromissoTitle.classList.add("no-compromissos");
                        container.innerHTML = `<div></div>`;
                        const colclassName = "agenda-item-col col-md-6 col-lg-auto mb-4"; // 4 colunas por linha
                        container.innerHTML = `
                            <div class="${colclassName || ""}">
                                <div class="agenda-item no-compromissos">
                                    <div class="agenda-item--title">Nenhum compromisso encontrado.</div>
                                </div>
                            </div>
                        `;
                    }
                    compromissosList.appendChild(container);
                })
                .catch(error => {
                    console.error("Erro ao buscar compromissos:", error);
                    compromissosList.innerHTML = `
                        <div class="col-12">
                            <div class="agenda-item">
                                <div class="agenda-item--title">Erro ao carregar compromissos.</div>
                            </div>
                        </div>
                    `;
                });
        }
    }

    // Verificar parâmetro 'data' na URL
    const urlParams = new URLSearchParams(window.location.search);
    const dataParam = urlParams.get('data');
    
    if (dataParam) {
        loadCompromissos(dataParam);
        calendar.set({ selectedDates: [new Date(dataParam)], });
    } else {
        // Seleciona a data atual e busca compromissos de hoje
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        const todayStr = `${yyyy}-${mm}-${dd}`;
        calendar.set({ selectedDates: [new Date()], });
        loadCompromissos(todayStr);
    }

    calendar.init();
  });