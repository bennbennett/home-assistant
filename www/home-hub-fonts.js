// Home Hub fonts + global animations loader
// Injects Google Fonts (Fraunces) and shared Home Hub animation keyframes
// into the document head. Loaded globally via frontend.extra_module_url in
// configuration.yaml.
//
// Fraunces is a contemporary serif with optical sizes — lends an editorial
// tone that complements the warm-neutral kitchen palette without feeling
// stuffy. Used for page headers and select large display elements; body
// text stays system sans for legibility.
//
// Animations live here so they're available across button-card JS templates
// (where styles can't be re-declared) without each card needing a card_mod
// keyframes block.

(function loadHomeHubFonts() {
  if (document.head.querySelector('link[data-home-hub-fonts]')) return;

  const preconnectGoogle = document.createElement('link');
  preconnectGoogle.rel = 'preconnect';
  preconnectGoogle.href = 'https://fonts.googleapis.com';
  preconnectGoogle.dataset.homeHubFonts = '1';

  const preconnectGstatic = document.createElement('link');
  preconnectGstatic.rel = 'preconnect';
  preconnectGstatic.href = 'https://fonts.gstatic.com';
  preconnectGstatic.crossOrigin = 'anonymous';
  preconnectGstatic.dataset.homeHubFonts = '1';

  // Fraunces variable font: opsz 9-144, weights 300-700 (with italics for emphasis later)
  const fraunces = document.createElement('link');
  fraunces.rel = 'stylesheet';
  fraunces.href = 'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600;9..144,700&display=swap';
  fraunces.dataset.homeHubFonts = '1';

  document.head.appendChild(preconnectGoogle);
  document.head.appendChild(preconnectGstatic);
  document.head.appendChild(fraunces);
})();

(function loadHomeHubAnimations() {
  if (document.head.querySelector('style[data-home-hub-anim]')) return;
  const style = document.createElement('style');
  style.dataset.homeHubAnim = '1';
  style.textContent = `
    @keyframes hh-pulse {
      0%   { box-shadow: 0 0 0 0 rgba(200, 116, 86, 0.55); }
      70%  { box-shadow: 0 0 0 8px rgba(200, 116, 86, 0); }
      100% { box-shadow: 0 0 0 0 rgba(200, 116, 86, 0); }
    }
    @keyframes hh-fade-in {
      from { opacity: 0; transform: translateY(4px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @media (prefers-reduced-motion: reduce) {
      @keyframes hh-pulse { from {} to {} }
      @keyframes hh-fade-in { from { opacity: 1; } to { opacity: 1; } }
    }
  `;
  document.head.appendChild(style);
})();

// Editorial Kitchen — warm overrides for the lovelace-hourly-weather card.
// The card defines its color variables on a `.main` selector inside its
// nested shadow root, so card-mod can't reach them from the parent. We
// patch each weather-bar's shadow root with a small <style> tag the first
// time we see it, and re-check periodically since these elements get
// recreated on view changes.
(function patchHourlyWeather() {
  const WARM_PATCH = `
    .main {
      --color-clear-night: #3D3654 !important;     /* warm dusk indigo */
      --color-cloudy: #B6B0A2 !important;           /* warm gray-tan */
      --color-partlycloudy: #C6D8E8 !important;     /* softer day blue */
      --color-sunny: #F5C57F !important;            /* honey yellow */
      --color-clear-night-foreground: #FBFAF9 !important;
      --color-cloudy-foreground: #1F2937 !important;
      --color-partlycloudy-foreground: #1F2937 !important;
      --color-sunny-foreground: #1F2937 !important;
    }
  `;

  function patchOne(wb) {
    if (!wb || !wb.shadowRoot) return;
    if (wb.shadowRoot.querySelector('style[data-home-hub-warm]')) return;
    const s = document.createElement('style');
    s.dataset.homeHubWarm = '1';
    s.textContent = WARM_PATCH;
    wb.shadowRoot.appendChild(s);
  }

  function findAll(root) {
    if (!root) return [];
    const out = [];
    const els = root.querySelectorAll ? root.querySelectorAll('*') : [];
    for (const el of els) {
      if (el.tagName && el.tagName.toLowerCase() === 'weather-bar') out.push(el);
      if (el.shadowRoot) out.push(...findAll(el.shadowRoot));
    }
    return out;
  }

  function sweep() {
    findAll(document.body).forEach(patchOne);
  }

  // Initial sweep + periodic re-check (cheap, only patches once per element)
  sweep();
  setInterval(sweep, 1500);
})();

// Countertop — vertical centering for sparse views (Lights, Toby).
// Layout is a 3-row grid: header (auto) | content (1fr) | scene bar (auto).
// The middle child is the grid/content card that should sit vertically
// centered in its 1fr row. CSS grid defaults to align-self: stretch, so we
// inject align-self: center on the middle child via its shadow root parent.
(function patchCountertopCentering() {
  const CENTERED_PATHS = ['/the-countertop/lights', '/the-countertop/toby'];

  function sweep() {
    if (!CENTERED_PATHS.includes(location.pathname)) return;

    // Walk: home-assistant > main > panel > root > panel-view > layout-card > grid-layout
    const ha = document.querySelector('home-assistant');
    if (!ha || !ha.shadowRoot) return;
    const main = ha.shadowRoot.querySelector('home-assistant-main');
    if (!main || !main.shadowRoot) return;
    const panel = main.shadowRoot.querySelector('ha-panel-lovelace');
    if (!panel || !panel.shadowRoot) return;
    const root = panel.shadowRoot.querySelector('hui-root');
    if (!root || !root.shadowRoot) return;
    const pv = root.shadowRoot.querySelector('hui-panel-view');
    if (!pv || !pv.shadowRoot) return;
    const lc = pv.shadowRoot.querySelector('layout-card');
    if (!lc || !lc.shadowRoot) return;
    const gl = lc.shadowRoot.querySelector('grid-layout');
    if (!gl || !gl.shadowRoot) return;
    const gridRoot = gl.shadowRoot.querySelector('#root');
    if (!gridRoot) return;

    // Center the middle child (row 2 of the auto/1fr/auto grid).
    const kids = gridRoot.children;
    if (kids.length >= 2) {
      const middle = kids[1];
      middle.style.setProperty('align-self', 'center', 'important');
      middle.style.setProperty('height', 'fit-content', 'important');
    }
  }

  sweep();
  setInterval(sweep, 2000);
})();

// Countertop — style short notifications like a real top-center toast instead
// of the default HA snackbar position. Browser Mod notification renders through
// ha-toast inside notification-manager, so we patch each toast host once and
// inject a small shadow-root style for the warm countertop treatment.
(function patchCountertopToasts() {
  const TOAST_PATCH = `
    .mdc-snackbar {
      justify-content: center !important;
    }
    .mdc-snackbar__surface {
      background: #C87456 !important;
      color: #FFFFFF !important;
      border-radius: 14px !important;
      box-shadow: 0 10px 26px rgba(200, 116, 86, 0.26) !important;
      min-height: 44px !important;
      padding: 0 18px !important;
    }
    .mdc-snackbar__label {
      color: #FFFFFF !important;
      font-size: 15px !important;
      font-weight: 600 !important;
      text-align: center !important;
      padding: 0 !important;
    }
    .mdc-snackbar__actions {
      display: none !important;
    }
  `;

  function patchOne(toast) {
    if (!toast) return;

    toast.style.position = 'fixed';
    toast.style.top = '22px';
    toast.style.left = '50%';
    toast.style.right = 'auto';
    toast.style.bottom = 'auto';
    toast.style.transform = 'translateX(-50%)';
    toast.style.width = 'auto';
    toast.style.maxWidth = '420px';
    toast.style.zIndex = '9999';
    toast.style.setProperty('--mdc-snackbar-container-color', '#C87456');
    toast.style.setProperty('--mdc-snackbar-supporting-text-color', '#FFFFFF');
    toast.style.setProperty('--mdc-snackbar-action-color', '#FFFFFF');

    if (!toast.shadowRoot || toast.shadowRoot.querySelector('style[data-ct-toast]')) return;

    const style = document.createElement('style');
    style.dataset.ctToast = '1';
    style.textContent = TOAST_PATCH;
    toast.shadowRoot.appendChild(style);
  }

  function findAll(root) {
    if (!root) return [];
    const out = [];
    const els = root.querySelectorAll ? root.querySelectorAll('*') : [];
    for (const el of els) {
      if (el.tagName && el.tagName.toLowerCase() === 'ha-toast') out.push(el);
      if (el.shadowRoot) out.push(...findAll(el.shadowRoot));
    }
    return out;
  }

  function sweep() {
    if (!location.pathname.startsWith('/the-countertop')) return;
    findAll(document.body).forEach(patchOne);
  }

  sweep();
  setInterval(sweep, 800);

  // MutationObserver for instant toast patching — catches transient toasts
  // that appear and disappear between interval sweeps
  var toastObserver = new MutationObserver(function(mutations) {
    if (!location.pathname.startsWith('/the-countertop')) return;
    mutations.forEach(function(m) {
      m.addedNodes.forEach(function(node) {
        if (!node.tagName) return;
        if (node.tagName.toLowerCase() === 'ha-toast') patchOne(node);
        if (node.querySelectorAll) {
          node.querySelectorAll('ha-toast').forEach(patchOne);
        }
      });
    });
  });
  toastObserver.observe(document.body, { childList: true, subtree: true });
})();

// Countertop — best-effort wake lock while the kitchen timer is actively
// running. This stays route-gated and silently no-ops where unsupported.
(function countertopWakeLock() {
  let wakeLock = null;

  function getHass() {
    const ha = document.querySelector('home-assistant');
    return ha && ha.hass ? ha.hass : null;
  }

  async function releaseLock() {
    if (!wakeLock) return;
    try {
      await wakeLock.release();
    } catch (err) {
      // Ignore release races from browser visibility changes.
    }
    wakeLock = null;
  }

  async function requestLock() {
    if (!('wakeLock' in navigator) || wakeLock || document.visibilityState !== 'visible') return;
    try {
      wakeLock = await navigator.wakeLock.request('screen');
      wakeLock.addEventListener('release', () => {
        wakeLock = null;
      });
    } catch (err) {
      wakeLock = null;
    }
  }

  async function sweep() {
    if (!location.pathname.startsWith('/the-countertop')) {
      releaseLock();
      return;
    }

    const hass = getHass();
    const timer = hass && hass.states ? hass.states['timer.kitchen_timer'] : null;
    const active = timer && timer.state === 'active';

    if (active) requestLock();
    else releaseLock();
  }

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') sweep();
    else releaseLock();
  });

  sweep();
  setInterval(sweep, 5000);
})();

// Countertop — patch HA-native input_text fields to remove MDC chrome.
// entities cards render input_text as hui-input-text-entity-row → ha-textfield
// → shadow root → .mdc-text-field. card_mod can't reach through ha-textfield's
// shadow boundary, so we inject a <style> tag directly into each shadow root.
// Uses the recursive walker pattern (like patchHourlyWeather) because popup
// inputs live inside browser-mod-popup elements appended to document.body
// outside the normal HA shadow DOM tree.
(function patchInputFields() {
  const INPUT_PATCH = `
    .mdc-text-field {
      border: 1px solid #E8E4DE !important;
      border-radius: 12px !important;
      background: white !important;
      height: 44px !important;
      padding: 0 14px !important;
      box-sizing: border-box !important;
    }
    .mdc-text-field--focused {
      border-color: #C87456 !important;
    }
    .mdc-line-ripple,
    .mdc-line-ripple::before,
    .mdc-line-ripple::after {
      display: none !important;
    }
    .mdc-floating-label {
      display: none !important;
    }
    .mdc-notched-outline,
    .mdc-notched-outline__leading,
    .mdc-notched-outline__notch,
    .mdc-notched-outline__trailing {
      display: none !important;
    }
    .mdc-text-field__input {
      font-size: 15px !important;
      font-weight: 400 !important;
      color: #1F2937 !important;
      caret-color: #C87456 !important;
      padding: 0 !important;
    }
    .mdc-text-field__ripple {
      display: none !important;
    }
    .mdc-text-field-helper-line,
    .mdc-text-field-helper-text,
    .mdc-text-field-character-counter {
      display: none !important;
    }
  `;

  function patchOne(row) {
    // Walk row's shadow tree to find an element by tag name. The original
    // patcher used row.querySelector() which only searches the light DOM,
    // but hui-input-text-entity-row renders ha-textfield (and state-badge)
    // INSIDE its own shadow root. Verified live 2026-04-11: row has its
    // own shadow root containing card-mod + hui-generic-entity-row, and
    // ha-textfield lives nested deeper in that subtree.
    function findInShadow(root, tag) {
      if (!root || !root.querySelectorAll) return null;
      var els = root.querySelectorAll('*');
      for (var i = 0; i < els.length; i++) {
        var el = els[i];
        if (el.tagName && el.tagName.toLowerCase() === tag) return el;
        if (el.shadowRoot) {
          var nested = findInShadow(el.shadowRoot, tag);
          if (nested) return nested;
        }
      }
      return null;
    }

    // Hide the leading state-badge icon (search both light and shadow trees)
    var badge = row.querySelector('state-badge') || findInShadow(row.shadowRoot, 'state-badge');
    if (badge) badge.style.display = 'none';

    // Find ha-textfield in the row
    var tf = row.querySelector('ha-textfield') || findInShadow(row.shadowRoot, 'ha-textfield');
    if (!tf || !tf.shadowRoot) return;
    if (tf.getAttribute('data-ct-patched')) return;
    tf.setAttribute('data-ct-patched', '1');
    tf.style.cssText = 'border:none !important;border-bottom:none !important;box-shadow:none !important;background:transparent !important;';

    // HA 2026.3+: ha-textfield contains <ha-input> (NOT MDC elements).
    // We style ha-input directly + dive into its shadow root for the native <input>.
    var haInput = tf.shadowRoot.querySelector('ha-input');
    if (!haInput) return;

    // Clear any default ha-input chrome — wa-input inside handles all visuals
    haInput.style.cssText = 'border:none;background:transparent;padding:0;box-shadow:none;';

    // HA 2026.3: ha-input > wa-input (Web Awesome) > actual input element
    // Dive through each shadow root level to reach and style the native input
    function patchHaInput() {
      if (!haInput.shadowRoot) return false;

      // Find wa-input inside ha-input's shadow root
      var waInput = haInput.shadowRoot.querySelector('wa-input');
      if (!waInput) return false;

      // Style wa-input container directly
      waInput.style.cssText = 'border:1px solid #E8E4DE !important;border-radius:12px !important;background:white !important;height:44px !important;box-sizing:border-box !important;';

      // Dive into wa-input's shadow root
      if (!waInput.shadowRoot) return false;
      if (waInput.shadowRoot.querySelector('style[data-ct-wa]')) return true;

      // Dump wa-input's shadow root once for diagnostics
      if (!waInput._ctDumped) {
        waInput._ctDumped = true;
        var innerTags = [];
        waInput.shadowRoot.querySelectorAll('*').forEach(function(el) {
          var info = el.tagName.toLowerCase();
          if (el.className && typeof el.className === 'string' && el.className) info += '.' + el.className.trim().split(/\s+/).join('.');
          innerTags.push(info);
        });
        console.log('[CT] wa-input shadowRoot elements:', innerTags.join(', '));
      }

      // Inject styles into wa-input's shadow root — exact selectors for HA 2026.3
      // wa-input contains: label.label, div.text-field, input.control, slots
      var waStyle = document.createElement('style');
      waStyle.dataset.ctWa = '1';
      waStyle.textContent = [
        ':host { border:1px solid #E8E4DE !important; border-radius:12px !important; background:white !important; height:44px !important; box-shadow:none !important; }',
        ':host(:focus-within) { border-color:#C87456 !important; }',
        '.label { display:none !important; }',
        '.text-field { border:none !important; background:transparent !important; box-shadow:none !important; padding:0 14px !important; height:100% !important; display:flex !important; align-items:center !important; }',
        '.text-field::before, .text-field::after { display:none !important; content:none !important; background:transparent !important; height:0 !important; }',
        'input.control { font-size:15px !important; color:#1F2937 !important; caret-color:#C87456 !important; border:none !important; outline:none !important; background:transparent !important; width:100% !important; padding:0 !important; }',
        'input.control::placeholder { color:#9CA3AF !important; }'
      ].join('\n');
      waInput.shadowRoot.appendChild(waStyle);

      // Set context-appropriate placeholder
      var nativeInput = waInput.shadowRoot.querySelector('input');
      if (nativeInput) {
        var hint = location.pathname.indexOf('/toby') !== -1 ? 'Add a new activity...' : 'Milk, eggs, bread...';
        nativeInput.placeholder = hint;
      }
      return true;
    }

    // Try immediately, retry if shadow root not ready
    if (!patchHaInput()) {
      var retries = 0;
      var retryId = setInterval(function() {
        if (patchHaInput() || ++retries > 15) clearInterval(retryId);
      }, 200);
    }
  }

  function findAll(root) {
    if (!root) return [];
    var out = [];
    var els = root.querySelectorAll ? root.querySelectorAll('*') : [];
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.tagName && el.tagName.toLowerCase() === 'hui-input-text-entity-row') out.push(el);
      if (el.shadowRoot) {
        var nested = findAll(el.shadowRoot);
        for (var j = 0; j < nested.length; j++) out.push(nested[j]);
      }
    }
    return out;
  }

  function sweep() {
    if (!location.pathname.startsWith('/the-countertop')) return;
    var found = findAll(document.body);
    if (found.length) console.log('[CT] patchInputFields:', location.pathname, found.length, 'inputs found');
    found.forEach(patchOne);
  }

  sweep();
  setInterval(sweep, 1500);
})();
