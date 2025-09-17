class CharCountController extends window.StimulusModule.Controller {
  static values = { max: { default: 220, type: Number } };

  connect() {
    this.setupOutput();
    this.updateCount();
    this.definedMaxValue = this.maxValue;
  }


  setupOutput() {
    if (this.output) return;
    const template = document.createElement('template');
    template.innerHTML = `<div class="charcount-wrapper" style="display: flex; justify-content: flex-end;">
            <output
                name='char-count'
                for='${this.element.id}'
                class='output-label'
            ></output>
        </div>`;
    const output = template.content.firstChild;
    this.element.insertAdjacentElement('afterend', output);
    this.output = output;
  }

  updateCount(event) {
    const value = event ? event.target.value : this.element.value;
    const chars = (value || '').length;
    const max = this.element.getAttribute('maxlength');
    this.definedMaxValue = this.maxValue ?? max;
    if (chars >= this.definedMaxValue) {
      this.output.style.color = 'red';
    } else if (chars > this.definedMaxValue * 0.8) {
      this.output.style.color = 'orange';
    } else {
      this.output.style.color = 'inherit';
    }
    this.output.textContent = `${chars} / ${this.definedMaxValue} caracteres`;
  }

  disconnect() {
    this.output && this.output.remove();
  }
}
window.wagtail.app.register('char-count', CharCountController);
