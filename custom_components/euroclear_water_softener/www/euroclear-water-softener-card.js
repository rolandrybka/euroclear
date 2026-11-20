class EuroclearWaterSoftenerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._confirming = false;
    this._sending = false;
    this._error = "";
    this.shadowRoot.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && this._confirming && !this._sending) {
        this._confirming = false;
        this._error = "";
        this._render();
      }
    });
  }

  setConfig(config) {
    if (!config.regeneration_button) {
      throw new Error("Please configure a regeneration_button entity.");
    }
    this._config = {
      title: config.title,
      subtitle: config.subtitle || "Midnight 25 HF P&P",
      regeneration_button: config.regeneration_button,
      metrics: config.metrics || [],
      alerts: config.alerts || [],
    };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 4;
  }

  _escape(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  _state(entityId) {
    return entityId && this._hass && this._hass.states
      ? this._hass.states[entityId]
      : undefined;
  }

  _render() {
    if (!this.shadowRoot || !this._config || !this._hass) {
      return;
    }

    const hu = (this._hass.language || "").toLowerCase().startsWith("hu");
    this._text = hu
      ? {
          sendError:
            "A parancs küldése nem sikerült. Ellenőrizd a Home Assistant naplóját, majd próbáld újra.",
        }
      : {
          sendError:
            "The command could not be sent. Check Home Assistant logs and try again.",
        };
    const text = hu
      ? {
          title: "Euroclear vízlágyító",
          noMetrics: "A kártya beállításainál adj meg szenzorokat.",
          noAlerts: "Nincs aktív riasztás",
          start: "Regenerálás indítása",
          confirmTitle: "Elindítod a regenerálást?",
          confirmMessage:
            "Ez azonnal elindít egy kényszerregenerálási ciklust, amely 5–6 órán át tarthat. Biztosan folytatod?",
          cancel: "Mégse",
          sending: "Küldés…",
        }
      : {
          title: "Euroclear water softener",
          noMetrics: "Add metrics in the card configuration.",
          noAlerts: "No active alerts",
          start: "Start forced regeneration",
          confirmTitle: "Start regeneration?",
          confirmMessage:
            "This starts a forced regeneration cycle, which may take 5–6 hours. Make sure you want to continue.",
          cancel: "Cancel",
          sending: "Sending…",
        };

    const metrics = this._config.metrics
      .map((metric) => {
        const state = this._state(metric.entity);
        const value = state ? state.state : "—";
        const unit = state?.attributes?.unit_of_measurement || "";
        const label = metric.label || state?.attributes?.friendly_name || metric.entity;
        const icon = metric.icon || "mdi:water-outline";
        return `
          <div class="metric">
            <ha-icon icon="${this._escape(icon)}"></ha-icon>
            <div class="metric-copy">
              <span class="metric-label">${this._escape(label)}</span>
              <span class="metric-value">${this._escape(value)}${unit ? ` <small>${this._escape(unit)}</small>` : ""}</span>
            </div>
          </div>`;
      })
      .join("");

    const activeAlerts = this._config.alerts
      .map((alert) => {
        const state = this._state(alert.entity);
        if (!state || state.state !== "on") {
          return "";
        }
        const label = alert.label || state.attributes.friendly_name || alert.entity;
        return `<div class="alert"><ha-icon icon="mdi:alert-circle"></ha-icon><span>${this._escape(label)}</span></div>`;
      })
      .join("");

    const button = this._state(this._config.regeneration_button);
    const unavailable = !button || button.state === "unavailable";
    const alerts = activeAlerts
      ? `<div class="alerts">${activeAlerts}</div>`
      : `<div class="all-clear"><ha-icon icon="mdi:check-circle-outline"></ha-icon><span>${text.noAlerts}</span></div>`;
    const dialog = this._confirming
      ? `<div class="scrim" role="presentation">
          <section class="dialog" role="alertdialog" aria-modal="true" aria-labelledby="dialog-title">
            <div class="dialog-icon"><ha-icon icon="mdi:water-sync"></ha-icon></div>
            <h2 id="dialog-title">${text.confirmTitle}</h2>
            <p>${text.confirmMessage}</p>
            ${this._error ? `<p class="error" role="alert">${this._escape(this._error)}</p>` : ""}
            <div class="dialog-actions">
              <button class="cancel" type="button" ${this._sending ? "disabled" : ""}>${text.cancel}</button>
              <button class="confirm" type="button" ${this._sending ? "disabled" : ""}>
                ${this._sending ? text.sending : text.start}
              </button>
            </div>
          </section>
        </div>`
      : "";

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card {
          overflow: hidden;
          color: var(--primary-text-color);
          background:
            radial-gradient(ellipse at 100% 0%, rgba(91, 190, 207, .16), transparent 42%),
            var(--ha-card-background, var(--card-background-color));
          border: 1px solid var(--divider-color);
          border-radius: 22px;
          box-shadow: var(--ha-card-box-shadow, 0 8px 26px rgba(0, 0, 0, .12));
        }
        .content { padding: 22px; }
        .heading { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
        .drop {
          display: grid; place-items: center; flex: 0 0 52px; height: 52px;
          color: #fff; border-radius: 18px;
          background: linear-gradient(145deg, #38b8c5, #247da9);
          box-shadow: 0 7px 17px rgba(36, 125, 169, .28);
        }
        .drop ha-icon { --mdc-icon-size: 30px; }
        h1 { margin: 0; font-size: 20px; line-height: 1.3; font-weight: 650; }
        .subtitle { display: block; margin-top: 3px; color: var(--secondary-text-color); font-size: 13px; }
        .metrics { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
        .metric {
          display: flex; align-items: center; gap: 11px; min-width: 0;
          padding: 13px; border: 1px solid var(--divider-color);
          border-radius: 15px; background: var(--secondary-background-color, rgba(127, 127, 127, .06));
        }
        .metric ha-icon { flex: 0 0 auto; color: var(--accent-color, #35a9ba); --mdc-icon-size: 22px; }
        .metric-copy { display: flex; flex-direction: column; min-width: 0; gap: 4px; }
        .metric-label { overflow: hidden; color: var(--secondary-text-color); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
        .metric-value { font-size: 17px; font-weight: 650; overflow-wrap: anywhere; }
        .metric-value small { color: var(--secondary-text-color); font-size: 12px; font-weight: 500; }
        .all-clear, .alert { display: flex; align-items: center; gap: 8px; margin-top: 14px; font-size: 13px; }
        .all-clear { color: var(--success-color, #398a63); }
        .alert { color: var(--error-color, #c33); }
        .all-clear ha-icon, .alert ha-icon { --mdc-icon-size: 19px; }
        .action { width: 100%; margin-top: 18px; padding: 12px 16px; border: 0; border-radius: 13px;
          color: #fff; background: linear-gradient(110deg, #247da9, #35a9ba);
          font: inherit; font-size: 14px; font-weight: 650; cursor: pointer; }
        .action:hover:not(:disabled) { filter: brightness(1.08); }
        button:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 3px; }
        button:disabled { cursor: not-allowed; opacity: .55; }
        .scrim { position: fixed; z-index: 9999; inset: 0; display: grid; place-items: center;
          padding: 20px; background: rgba(0, 0, 0, .56); }
        .dialog { box-sizing: border-box; width: min(440px, 100%); padding: 24px;
          color: var(--primary-text-color); background: var(--ha-card-background, var(--card-background-color));
          border-radius: 22px; box-shadow: 0 18px 60px rgba(0, 0, 0, .3); }
        .dialog-icon { display: grid; place-items: center; width: 48px; height: 48px; margin-bottom: 14px;
          color: var(--warning-color, #bd7918); border-radius: 16px; background: rgba(189, 121, 24, .12); }
        .dialog-icon ha-icon { --mdc-icon-size: 26px; }
        h2 { margin: 0 0 8px; font-size: 20px; }
        .dialog p { color: var(--secondary-text-color); font-size: 14px; line-height: 1.55; }
        .dialog .error { color: var(--error-color, #c33); }
        .dialog-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 22px; }
        .dialog-actions button { min-height: 42px; padding: 0 14px; border: 0; border-radius: 11px;
          font: inherit; font-weight: 600; cursor: pointer; }
        .cancel { color: var(--primary-text-color); background: var(--secondary-background-color, rgba(127, 127, 127, .12)); }
        .confirm { color: #fff; background: var(--error-color, #bd4d43); }
        @media (max-width: 420px) {
          .content { padding: 17px; }
          .metrics { gap: 8px; }
          .metric { padding: 10px; gap: 8px; }
          .metric-value { font-size: 15px; }
          .dialog-actions { flex-direction: column-reverse; }
          .dialog-actions button { width: 100%; }
        }
      </style>
      <ha-card>
        <div class="content">
          <header class="heading">
            <div class="drop"><ha-icon icon="mdi:water"></ha-icon></div>
            <div>
              <h1>${this._escape(this._config.title || text.title)}</h1>
              <span class="subtitle">${this._escape(this._config.subtitle)}</span>
            </div>
          </header>
          <div class="metrics">${metrics || `<div class="empty">${text.noMetrics}</div>`}</div>
          ${alerts}
          <button class="action" type="button" ${unavailable || this._sending ? "disabled" : ""}>
            <ha-icon icon="mdi:water-sync"></ha-icon>
            ${text.start}
          </button>
        </div>
      </ha-card>
      ${dialog}`;

    this.shadowRoot.querySelector(".action").addEventListener("click", () => {
      this._confirming = true;
      this._error = "";
      this._render();
    });

    if (this._confirming) {
      this.shadowRoot.querySelector(".cancel").addEventListener("click", () => {
        this._confirming = false;
        this._error = "";
        this._render();
      });
      this.shadowRoot.querySelector(".cancel").focus();
      this.shadowRoot.querySelector(".confirm").addEventListener("click", () => {
        this._startRegeneration();
      });
      this.shadowRoot.querySelector(".scrim").addEventListener("click", (event) => {
        if (event.target.classList.contains("scrim") && !this._sending) {
          this._confirming = false;
          this._error = "";
          this._render();
        }
      });
    }
  }

  async _startRegeneration() {
    this._sending = true;
    this._error = "";
    this._render();
    try {
      await this._hass.callService("button", "press", {
        entity_id: this._config.regeneration_button,
      });
      this._confirming = false;
    } catch (error) {
      console.error("Could not start water softener regeneration", error);
      this._error = this._text.sendError;
    } finally {
      this._sending = false;
      this._render();
    }
  }
}

if (!customElements.get("euroclear-water-softener-card")) {
  customElements.define("euroclear-water-softener-card", EuroclearWaterSoftenerCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "euroclear-water-softener-card",
    name: "Euroclear Water Softener",
    description: "Water softener status card with regeneration confirmation.",
  });
}
