/**
 * Custom Lovelace card for embedding OpenProject interface via iframe
 * 
 * Installation:
 * 1. Copy this file to /config/www/openproject-card.js
 * 2. Add resource in Lovelace dashboard configuration:
 *    resources:
 *      - url: /local/openproject-card.js
 *        type: module
 * 3. Use in dashboard:
 *    type: custom:openproject-iframe-card
 *    title: OpenProject
 *    height: 800
 */

class OpenProjectIframeCard extends HTMLElement {
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
    const openprojectUrl = this.config.openproject_url || '/api/home_ops_bridge/openproject_proxy/';

    const card = document.createElement('ha-card');
    card.innerHTML = `
      <div class="card-header">
        <div class="name">${this.config.title || 'OpenProject'}</div>
      </div>
      <div class="card-content">
        <iframe 
          src="${openprojectUrl}"
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
    let element = document.querySelector('openproject-iframe-card-editor');
    if (!element) {
      element = document.createElement('openproject-iframe-card-editor');
    }
    return element;
  }

  static getStubConfig() {
    return {
      type: 'custom:openproject-iframe-card',
      title: 'OpenProject',
      height: 800,
    };
  }
}

customElements.define('openproject-iframe-card', OpenProjectIframeCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'openproject-iframe-card',
  name: 'OpenProject Iframe',
  description: 'Embed OpenProject interface via iframe proxy',
  preview: true,
});
