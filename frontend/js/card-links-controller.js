class CardLinksController extends window.StimulusModule.Controller {
  static values = {
    toggleField: String,
    targetFields: String
  };

  connect() {
    this.toggleInput = this.#findFieldInput(this.toggleFieldValue);
    if (!this.toggleInput) {
      return;
    }

    this.targetConfigs = this.#buildTargetConfigs();
    if (!this.targetConfigs.length) {
      return;
    }

    this.boundUpdateState = this.#updateState.bind(this);
    this.toggleInput.addEventListener('change', this.boundUpdateState);

    this.#updateState();
  }

  disconnect() {
    if (this.toggleInput && this.boundUpdateState) {
      this.toggleInput.removeEventListener('change', this.boundUpdateState);
    }
  }

  #buildTargetConfigs() {
    if (!this.targetFieldsValue) {
      return [];
    }

    return this.targetFieldsValue
      .split(',')
      .map((name) => name.trim())
      .filter(Boolean)
      .map((fieldName) => {
        const container = this.#findFieldContainer(fieldName);
        if (!container) {
          return null;
        }

        const inputs = container.querySelectorAll('input, textarea, select, button');
        const message = this.#buildMessage(fieldName);

        return { container, inputs, message };
      })
      .filter(Boolean);
  }

  #findFieldInput(fieldName) {
    if (!fieldName) {
      return null;
    }

    return this.element.querySelector(`input[name$="-${fieldName}"]`);
  }

  #findFieldContainer(fieldName) {
    const input = this.element.querySelector(`[name$="-${fieldName}"]`);
    if (!input) {
      return null;
    }

    return input.closest('[data-field-path]') || input.closest('.w-field');
  }

  #buildMessage(fieldName) {
    const hint = document.createElement('p');
    hint.className = 'help-block';
    hint.dataset.cardLinksMessage = 'true';
    hint.textContent = 'Ative "Adicionar link" para preencher este campo';
    return hint;
  }

  #updateState() {
    const enabled = Boolean(this.toggleInput?.checked);

    this.targetConfigs.forEach(({ container, inputs, message }) => {
      inputs.forEach((input) => {
        input.disabled = !enabled;
      });

      if (!enabled) {
        if (!container.querySelector('[data-card-links-message="true"]')) {
          container.appendChild(message.cloneNode(true));
        }
        container.classList.add('card-links--disabled');
      } else {
        container.classList.remove('card-links--disabled');
        const existingMessage = container.querySelector('[data-card-links-message="true"]');
        if (existingMessage) {
          existingMessage.remove();
        }
      }
    });
  }
}

window.wagtail.app.register('card-links', CardLinksController);
