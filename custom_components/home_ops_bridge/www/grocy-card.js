/**
 * Custom Lovelace card for embedding Grocy interface via iframe
 * 
 * Installation:
 * 1. Copy this file to /config/www/grocy-card.js
 * 2. Add resource in Lovelace dashboard configuration:
 *    resources:
 *      - url: /local/grocy-card.js
 *        type: module
 * 3. Use in dashboard:
 *    type: custom:grocy-iframe-card
 *    title: Grocy
 *    height: 800
 */

class GrocyIframeCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  render() {
    if (!this._hass) return;

    // Use Home Ops Bridge proxy endpoint
    const grocyUrl = this.config.grocy_url || '/api/home_ops_bridge/grocy_proxy/';

    const card = document.createElement('ha-card');
    card.innerHTML = `
      <div class="card-header">
        <div class="name">${this.config.title || 'Grocy'}</div>
      </div>
      <div class="card-content">
        <iframe 
          src="${grocyUrl}"
          style="border: none; width: 100%; height: ${this.config.height || 800}px;"
          allow="same-origin"
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-cookies"
        ></iframe>
      </div>
    `;

    // Copy styles
    const style = document.createElement('style');
    style.textContent = `
      ha-card {
        overflow: hidden;
      }
      .card-header {
        padding: 16px;
        font-weight: 500;
        font-size: 1.1em;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
      }
      .card-content {
        padding: 0;
      }
    `;

    this.innerHTML = '';
    this.appendChild(style);
    this.appendChild(card);
  }

  getCardSize() {
    const height = this.config.height || 800;
    return Math.ceil(height / 50) + 2;
  }

  static getConfigElement() {
    let element = document.querySelector('grocy-iframe-card-editor');
    if (!element) {
      element = document.createElement('grocy-iframe-card-editor');
    }
    return element;
  }

  static getStubConfig() {
    return {
      type: 'custom:grocy-iframe-card',
      title: 'Grocy',
      height: 800,
    };
  }
}

customElements.define('grocy-iframe-card', GrocyIframeCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'grocy-iframe-card',
  name: 'Grocy Iframe',
  description: 'Embed Grocy interface via iframe proxy',
  preview: true,
});
