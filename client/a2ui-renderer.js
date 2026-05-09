/**
 * A2UI Renderer — converts A2UI v0.9 JSON messages into DOM elements.
 *
 * This is a minimal renderer to demonstrate how A2UI works:
 *   1. createSurface  → creates a container for a UI surface
 *   2. updateComponents → defines the component tree (flat list with ID refs)
 *   3. updateDataModel → populates data that components bind to
 *
 * The key A2UI insight: components are a FLAT list with IDs. Children reference
 * parent components by ID, not by nesting. This makes it easy for LLMs to
 * generate incrementally and for renderers to update individual components.
 */

let _rendererCounter = 0;

class A2UIRenderer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.surfaces = {};
    this.onAction = null;
    this.rawMessages = [];
    this._instanceId = ++_rendererCounter;
  }

  processMessages(messages) {
    if (!Array.isArray(messages)) messages = [messages];

    this.rawMessages.push(...messages);
    this._updateDebugPanel();

    for (const msg of messages) {
      if (msg.createSurface) {
        this._handleCreateSurface(msg.createSurface);
      } else if (msg.updateComponents) {
        this._handleUpdateComponents(msg.updateComponents);
      } else if (msg.updateDataModel) {
        this._handleUpdateDataModel(msg.updateDataModel);
      }
    }
  }

  clearSurfaces() {
    while (this.container.firstChild) {
      this.container.removeChild(this.container.firstChild);
    }
    this.surfaces = {};
    this.rawMessages = [];
    this._updateDebugPanel();
  }

  _handleCreateSurface({ surfaceId, theme }) {
    this.surfaces[surfaceId] = {
      components: {},
      dataModel: {},
      theme: theme || {},
    };
  }

  _handleUpdateComponents({ surfaceId, components }) {
    const surface = this.surfaces[surfaceId];
    if (!surface) return;

    for (const comp of components) {
      surface.components[comp.id] = comp;
    }
    this._renderSurface(surfaceId);
  }

  _handleUpdateDataModel({ surfaceId, path, value }) {
    const surface = this.surfaces[surfaceId];
    if (!surface) return;

    if (path === '/') {
      Object.assign(surface.dataModel, value);
    } else {
      const key = path.startsWith('/') ? path.substring(1) : path;
      surface.dataModel[key] = value;
    }
    this._renderSurface(surfaceId);
  }

  _renderSurface(surfaceId) {
    const surface = this.surfaces[surfaceId];
    if (!surface) return;

    const domId = `surface-${this._instanceId}-${surfaceId}`;
    let surfaceEl = document.getElementById(domId);
    if (!surfaceEl) {
      surfaceEl = document.createElement('div');
      surfaceEl.id = domId;
      surfaceEl.className = 'a2ui-surface';
      this.container.appendChild(surfaceEl);
    }

    const root = surface.components['root'];
    if (!root) return;

    while (surfaceEl.firstChild) {
      surfaceEl.removeChild(surfaceEl.firstChild);
    }
    const el = this._renderComponent(root, surface, surface.dataModel);
    if (el) surfaceEl.appendChild(el);
  }

  _renderComponent(comp, surface, dataContext) {
    switch (comp.component) {
      case 'Column':  return this._renderColumn(comp, surface, dataContext);
      case 'Row':     return this._renderRow(comp, surface, dataContext);
      case 'Card':    return this._renderCard(comp, surface, dataContext);
      case 'Text':    return this._renderText(comp, surface, dataContext);
      case 'Button':  return this._renderButton(comp, surface, dataContext);
      case 'Divider': return this._renderDivider();
      case 'List':    return this._renderList(comp, surface, dataContext);
      case 'TextField': return this._renderTextField(comp, surface, dataContext);
      case 'ChoicePicker': return this._renderChoicePicker(comp, surface, dataContext);
      case 'DateTimeInput': return this._renderDateTimeInput(comp, surface, dataContext);
      case 'Image':   return this._renderImage(comp, surface, dataContext);
      case 'Tabs':    return this._renderTabs(comp, surface, dataContext);
      case 'Modal':   return this._renderModal(comp, surface, dataContext);
      case 'CheckBox': return this._renderCheckBox(comp, surface, dataContext);
      case 'Slider':  return this._renderSlider(comp, surface, dataContext);
      case 'Icon':    return this._renderIcon(comp, surface, dataContext);
      case 'Video':   return this._renderVideo(comp, surface, dataContext);
      case 'AudioPlayer': return this._renderAudioPlayer(comp, surface, dataContext);
      default:
        const el = document.createElement('div');
        el.textContent = `[Unknown: ${comp.component}]`;
        return el;
    }
  }

  _renderColumn(comp, surface, dataContext) {
    const el = document.createElement('div');
    el.className = 'a2ui-column';
    this._renderChildren(comp.children, surface, dataContext, el);
    return el;
  }

  _renderRow(comp, surface, dataContext) {
    const el = document.createElement('div');
    el.className = 'a2ui-row';
    this._renderChildren(comp.children, surface, dataContext, el);
    return el;
  }

  _renderCard(comp, surface, dataContext) {
    const el = document.createElement('div');
    el.className = 'a2ui-card';
    if (comp.child) {
      const childComp = surface.components[comp.child];
      if (childComp) {
        const childEl = this._renderComponent(childComp, surface, dataContext);
        if (childEl) el.appendChild(childEl);
      }
    }
    return el;
  }

  _renderText(comp, surface, dataContext) {
    const el = document.createElement('span');
    const variant = comp.variant || 'body';
    el.className = `a2ui-text-${variant}`;

    let text = this._resolveValue(comp.text, surface, dataContext);
    el.textContent = text || '';

    if (comp.weight) el.style.flex = comp.weight;

    if (typeof text === 'string') {
      if (text.startsWith('+$') || (text.startsWith('$') && !text.startsWith('-'))) {
        el.classList.add('amount-positive');
      } else if (text.startsWith('-$')) {
        el.classList.add('amount-negative');
      }
    }

    return el;
  }

  _renderButton(comp, surface, dataContext) {
    const el = document.createElement('button');
    const variant = comp.variant || 'default';
    el.className = `a2ui-button a2ui-button-${variant}`;

    if (comp.child) {
      const childComp = surface.components[comp.child];
      if (childComp) {
        el.textContent = this._resolveValue(childComp.text, surface, dataContext) || '';
      }
    }

    if (comp.action && comp.action.event) {
      el.addEventListener('click', () => {
        const event = comp.action.event;
        const context = {};
        if (event.context) {
          for (const [key, val] of Object.entries(event.context)) {
            context[key] = this._resolveValue(val, surface, dataContext);
          }
        }
        if (this.onAction) {
          this.onAction(event.name, context);
        }
      });
    }

    return el;
  }

  _renderDivider() {
    return document.createElement('hr');
  }

  _renderList(comp, surface, dataContext) {
    const el = document.createElement('div');
    el.className = `a2ui-list ${comp.direction === 'horizontal' ? 'horizontal' : ''}`;

    if (comp.children && typeof comp.children === 'object' && comp.children.componentId) {
      const templateComp = surface.components[comp.children.componentId];
      const itemsPath = comp.children.path;
      const items = this._resolveValue({ path: itemsPath }, surface, dataContext);

      if (Array.isArray(items) && templateComp) {
        for (const item of items) {
          const itemEl = this._renderComponent(templateComp, surface, item);
          if (itemEl) el.appendChild(itemEl);
        }
      }
    } else if (Array.isArray(comp.children)) {
      this._renderChildren(comp.children, surface, dataContext, el);
    }

    return el;
  }

  _renderTextField(comp, surface, dataContext) {
    const wrapper = document.createElement('div');
    wrapper.className = 'a2ui-textfield';

    if (comp.label) {
      const label = document.createElement('label');
      label.textContent = comp.label;
      wrapper.appendChild(label);
    }

    const input = comp.variant === 'longText'
      ? document.createElement('textarea')
      : document.createElement('input');

    if (comp.variant === 'number') input.type = 'number';
    else if (comp.variant === 'obscured') input.type = 'password';
    else input.type = 'text';

    const currentVal = this._resolveValue(comp.value, surface, dataContext);
    if (currentVal) input.value = currentVal;

    if (comp.value && comp.value.path) {
      input.addEventListener('input', () => {
        this._setDataValue(comp.value.path, input.value, surface, dataContext);
      });
    }

    wrapper.appendChild(input);
    return wrapper;
  }

  _renderChoicePicker(comp, surface, dataContext) {
    const wrapper = document.createElement('div');
    wrapper.className = 'a2ui-choice-picker';

    if (comp.label) {
      const label = document.createElement('label');
      label.textContent = comp.label;
      wrapper.appendChild(label);
    }

    const select = document.createElement('select');
    const defaultOpt = document.createElement('option');
    defaultOpt.value = '';
    defaultOpt.textContent = 'Select...';
    select.appendChild(defaultOpt);

    const options = this._resolveValue(comp.options, surface, dataContext);
    if (Array.isArray(options)) {
      for (const opt of options) {
        const option = document.createElement('option');
        option.value = typeof opt === 'string' ? opt : opt.value;
        option.textContent = typeof opt === 'string' ? opt : opt.label;
        select.appendChild(option);
      }
    }

    const currentVal = this._resolveValue(comp.value, surface, dataContext);
    if (currentVal) select.value = currentVal;

    if (comp.value && comp.value.path) {
      select.addEventListener('change', () => {
        this._setDataValue(comp.value.path, select.value, surface, dataContext);
      });
    }

    wrapper.appendChild(select);
    return wrapper;
  }

  _renderDateTimeInput(comp, surface, dataContext) {
    const wrapper = document.createElement('div');
    wrapper.className = 'a2ui-datetime';

    if (comp.label) {
      const label = document.createElement('label');
      label.textContent = comp.label;
      wrapper.appendChild(label);
    }

    const input = document.createElement('input');
    if (comp.enableDate && comp.enableTime) input.type = 'datetime-local';
    else if (comp.enableDate) input.type = 'date';
    else if (comp.enableTime) input.type = 'time';
    else input.type = 'datetime-local';

    const currentVal = this._resolveValue(comp.value, surface, dataContext);
    if (currentVal) input.value = currentVal;

    if (comp.value && comp.value.path) {
      input.addEventListener('change', () => {
        this._setDataValue(comp.value.path, input.value, surface, dataContext);
      });
    }

    wrapper.appendChild(input);
    return wrapper;
  }

  _renderImage(comp, surface, dataContext) {
    const el = document.createElement('img');
    el.src = this._resolveValue(comp.url, surface, dataContext) || '';
    el.style.maxWidth = '100%';
    el.style.borderRadius = '8px';
    if (comp.variant === 'mediumFeature') {
      el.style.width = '120px';
      el.style.height = '80px';
      el.style.objectFit = 'cover';
    }
    return el;
  }

  _renderTabs(comp, surface, dataContext) {
    const wrapper = document.createElement('div');
    wrapper.className = 'a2ui-tabs';

    const tabBar = document.createElement('div');
    tabBar.className = 'a2ui-tab-bar';
    wrapper.appendChild(tabBar);

    const tabContent = document.createElement('div');
    tabContent.className = 'a2ui-tab-content';
    wrapper.appendChild(tabContent);

    const tabs = comp.tabs || [];
    tabs.forEach((tab, index) => {
      const tabBtn = document.createElement('button');
      tabBtn.className = 'a2ui-tab-btn' + (index === 0 ? ' active' : '');
      tabBtn.textContent = this._resolveValue(tab.title || tab.label, surface, dataContext) || ('Tab ' + (index + 1));
      tabBar.appendChild(tabBtn);

      const panel = document.createElement('div');
      panel.className = 'a2ui-tab-panel' + (index === 0 ? '' : ' hidden');

      if (tab.child) {
        const childComp = surface.components[tab.child];
        if (childComp) {
          const childEl = this._renderComponent(childComp, surface, dataContext);
          if (childEl) panel.appendChild(childEl);
        }
      } else if (tab.children) {
        this._renderChildren(tab.children, surface, dataContext, panel);
      }

      tabContent.appendChild(panel);

      tabBtn.addEventListener('click', () => {
        tabBar.querySelectorAll('.a2ui-tab-btn').forEach(b => b.classList.remove('active'));
        tabContent.querySelectorAll('.a2ui-tab-panel').forEach(p => p.classList.add('hidden'));
        tabBtn.classList.add('active');
        panel.classList.remove('hidden');
      });
    });

    return wrapper;
  }

  _renderModal(comp, surface, dataContext) {
    const el = document.createElement('div');
    if (comp.child) {
      const childComp = surface.components[comp.child];
      if (childComp) {
        const childEl = this._renderComponent(childComp, surface, dataContext);
        if (childEl) el.appendChild(childEl);
      }
    }
    return el;
  }

  _renderCheckBox(comp, surface, dataContext) {
    const wrapper = document.createElement('label');
    wrapper.className = 'a2ui-checkbox';

    const input = document.createElement('input');
    input.type = 'checkbox';
    const val = this._resolveValue(comp.value, surface, dataContext);
    input.checked = val === 'true' || val === true;

    if (comp.value && comp.value.path) {
      input.addEventListener('change', () => {
        this._setDataValue(comp.value.path, input.checked, surface, dataContext);
      });
    }

    const label = document.createElement('span');
    label.textContent = this._resolveValue(comp.label, surface, dataContext) || '';

    wrapper.appendChild(input);
    wrapper.appendChild(label);
    return wrapper;
  }

  _renderSlider(comp, surface, dataContext) {
    const wrapper = document.createElement('div');
    wrapper.className = 'a2ui-textfield';

    if (comp.label) {
      const label = document.createElement('label');
      label.textContent = this._resolveValue(comp.label, surface, dataContext);
      wrapper.appendChild(label);
    }

    const input = document.createElement('input');
    input.type = 'range';
    input.min = comp.min || 0;
    input.max = comp.max || 100;
    const val = this._resolveValue(comp.value, surface, dataContext);
    if (val) input.value = val;

    if (comp.value && comp.value.path) {
      input.addEventListener('input', () => {
        this._setDataValue(comp.value.path, input.value, surface, dataContext);
      });
    }

    wrapper.appendChild(input);
    return wrapper;
  }

  _renderIcon(comp, surface, dataContext) {
    const el = document.createElement('span');
    el.className = 'material-icons';
    el.textContent = this._resolveValue(comp.icon || comp.name, surface, dataContext) || 'help';
    return el;
  }

  _renderVideo(comp, surface, dataContext) {
    const el = document.createElement('video');
    el.src = this._resolveValue(comp.url, surface, dataContext) || '';
    el.controls = true;
    el.style.maxWidth = '100%';
    el.style.borderRadius = '8px';
    return el;
  }

  _renderAudioPlayer(comp, surface, dataContext) {
    const el = document.createElement('audio');
    el.src = this._resolveValue(comp.url, surface, dataContext) || '';
    el.controls = true;
    el.style.width = '100%';
    return el;
  }

  _renderChildren(children, surface, dataContext, parentEl) {
    if (!Array.isArray(children)) return;
    for (const childId of children) {
      const childComp = surface.components[childId];
      if (childComp) {
        const childEl = this._renderComponent(childComp, surface, dataContext);
        if (childEl) {
          if (childComp.weight) childEl.style.flex = childComp.weight;
          parentEl.appendChild(childEl);
        }
      }
    }
  }

  /**
   * Resolves a value — the core of A2UI data binding.
   * Values can be:
   *   - A literal string/number: "Hello" or 42
   *   - A path reference: { "path": "/title" } or { "path": "name" }
   *
   * Paths starting with "/" look up from the surface's dataModel.
   * Paths without "/" look up from the current item context (for lists).
   */
  _resolveValue(val, surface, dataContext) {
    if (val === null || val === undefined) return '';
    if (typeof val === 'string' || typeof val === 'number' || typeof val === 'boolean') return String(val);

    if (typeof val !== 'object') return String(val);

    // Path reference: { "path": "/title" } or { "path": "name" }
    // Per v0.9 spec: absolute paths (starting with /) resolve from dataModel root.
    // Relative paths resolve from current dataContext (list item scope).
    if (val.path) {
      const path = val.path;
      let resolved;
      if (path.startsWith('/')) {
        resolved = this._resolvePath(path.substring(1), surface.dataModel);
      } else {
        resolved = dataContext ? this._resolvePath(path, dataContext) : undefined;
      }
      if (resolved === null || resolved === undefined) return '';
      if (typeof resolved === 'object' && !Array.isArray(resolved)) return JSON.stringify(resolved);
      if (Array.isArray(resolved)) return resolved;
      return String(resolved);
    }

    // Function call: { "call": "formatString", "args": { "value": "..." } }
    if (val.call) {
      return this._evaluateFunction(val, surface, dataContext);
    }

    // Fallback: stringify any other object so it doesn't show [object Object]
    return JSON.stringify(val);
  }

  /**
   * Evaluates an A2UI FunctionCall: { call, args, returnType }
   * Per v0.9 spec, args values can be literals, path references, or nested function calls.
   * All args are resolved through _resolveValue before the function runs.
   */
  _evaluateFunction(funcDef, surface, dataContext) {
    const name = funcDef.call;
    const rawArgs = funcDef.args || {};

    // Resolve every arg value through the data binding system
    const resolved = {};
    for (const [key, val] of Object.entries(rawArgs)) {
      resolved[key] = this._resolveValue(val, surface, dataContext);
    }

    switch (name) {
      case 'formatString': {
        let template = resolved.value || '';
        // Replace ${path} interpolations in the template string
        return String(template).replace(/\$\{([^}]+)\}/g, (_, expr) => {
          // ${/absolute/path} or ${relativePath}
          const v = this._resolveValue({ path: expr }, surface, dataContext);
          return v !== undefined && v !== '' ? String(v) : '';
        });
      }

      case 'formatCurrency': {
        const num = parseFloat(resolved.value);
        if (isNaN(num)) return resolved.value || '';
        const currency = resolved.currency || 'USD';
        try {
          return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(num);
        } catch {
          return '$' + num.toFixed(2);
        }
      }

      case 'formatNumber': {
        const num = parseFloat(resolved.value);
        if (isNaN(num)) return resolved.value || '';
        return new Intl.NumberFormat('en-US').format(num);
      }

      case 'formatDate': {
        const format = resolved.format || '';
        const dateStr = resolved.value || '';
        if (!dateStr) return '';
        try {
          const date = new Date(dateStr);
          if (isNaN(date.getTime())) return dateStr;
          if (format === 'yyyy-MM-dd') return date.toISOString().split('T')[0];
          return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        } catch {
          return dateStr;
        }
      }

      case 'required':
      case 'regex':
      case 'email':
      case 'length':
      case 'numeric':
        return !!resolved.value;

      case 'and':
        return resolved.left && resolved.right;
      case 'or':
        return resolved.left || resolved.right;
      case 'not':
        return !resolved.value;

      case 'pluralize':
        return parseFloat(resolved.count) === 1
          ? (resolved.singular || '')
          : (resolved.plural || '');

      case 'openUrl':
        return '';

      default:
        // Unknown function — return resolved value if available
        return resolved.value !== undefined ? String(resolved.value) : '';
    }
  }

  _resolvePath(path, obj) {
    if (!obj || !path) return undefined;
    const parts = path.split('/').filter(Boolean);
    let current = obj;
    for (const part of parts) {
      if (current === null || current === undefined) return undefined;
      current = current[part];
    }
    return current;
  }

  _setDataValue(path, value, surface, dataContext) {
    if (path.startsWith('/')) {
      const key = path.substring(1);
      surface.dataModel[key] = value;
    } else if (dataContext) {
      dataContext[path] = value;
    }
  }

  _updateDebugPanel() {
    const el = document.getElementById('debug-json');
    if (el) {
      el.textContent = JSON.stringify(this.rawMessages, null, 2);
    }
  }
}
