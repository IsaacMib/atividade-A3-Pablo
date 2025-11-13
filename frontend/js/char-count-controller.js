class CharCountController extends window.StimulusModule.Controller {
  static get values() {
    return {
      // Default max length if not specified per field
      max: { default: 255, type: Number },
      // Format: "field1:100,field2:200" or just "field1,field2" to use default max
      fields: { type: String, default: '' }
    };
  }

  connect() {
    this.setupCounters();
  }

  setupCounters() {
    if (!this.fieldsValue) {
      this.addCounter(this.element, this.maxValue);
    }

    // Create a map of field names to their max lengths
    const fieldConfigs = this.fieldsValue.split(',').reduce((acc, config) => {
      const [fieldName, max] = config.trim().split(':');
      if (fieldName) {
        acc[fieldName] = max ? parseInt(max, 10) : this.maxValue;
      }
      return acc;
    }, {});

    Object.entries(fieldConfigs).forEach(([fieldName, maxLength]) => {
      const fields = this.element.querySelectorAll(`
        input[name$="-${fieldName}"], 
        textarea[name$="-${fieldName}"]
      `);
      
      fields.forEach(field => {
        if (field.dataset.charCountInitialized) return;
        field.dataset.charCountInitialized = 'true';
        this.addCounter(field, maxLength);
      });
    });
  }

  addCounter(field, maxLength) {
    // O maxlength do campo deve ser definido pelo widget para sobrecrever o campo título das páginas
    if (field.hasAttribute('maxlength')) {
      if (maxLength === undefined) {
        maxLength = field.getAttribute('maxlength');
      }
      else if (field.getAttribute('maxlength') != maxLength) {
        console.log(`O limite de caracteres do campo ${field.name} já havia sido estabelecido em ${field.getAttribute('maxlength')} e não coincide com o valor definido no controller ${maxLength}.`);
      }
    }
    field.setAttribute('maxlength', maxLength);

    const counter = document.createElement('div');
    counter.className = 'char-counter';
    counter.style.textAlign = 'right';
    counter.style.marginTop = '0.25rem';
    counter.style.fontSize = '0.875rem';
    counter.style.color = '#6c757d';
    
    field.closest('[data-field-input]').appendChild(counter);
    
    const update = () => {
      const length = (field.value || '').length;
      const remaining = maxLength - length;
      
      counter.textContent = `${length} / ${maxLength}`;
      
      counter.style.color = remaining <= 0 ? 'red' :
                          remaining < maxLength * 0.2 ? 'orange' :
                          'grey';
    };
    
    field.addEventListener('input', update);
    field.addEventListener('change', update);
    update();
  }
}

window.wagtail.app.register('char-count', CharCountController);