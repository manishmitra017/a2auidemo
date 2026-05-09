const AGENT_URL = 'http://localhost:10002';
const A2UI_EXTENSION_URI = 'https://a2ui.org/a2a-extension/a2ui/v0.9';
let taskContextId = null;
let requesting = false;
let responseCount = 0;

function handleSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text || requesting) return;
  input.value = '';
  sendTextToAgent(text);
}

function sendSuggestion(btn) {
  sendTextToAgent(btn.textContent);
}

async function sendTextToAgent(text) {
  hideWelcome();
  appendToChatFlow('user', text);
  showLoading();

  const parts = [
    { kind: 'text', text: text },
    { kind: 'data', data: { useStreaming: false } },
  ];

  await callAgent(parts);
}

async function sendActionToAgent(actionName, context) {
  showLoading();

  const parts = [
    {
      kind: 'data',
      data: {
        version: 'v0.9',
        action: { name: actionName, context: context },
      },
    },
    { kind: 'data', data: { useStreaming: false } },
  ];

  await callAgent(parts);
}

async function callAgent(parts) {
  requesting = true;
  document.getElementById('send-btn').disabled = true;

  try {
    const cardResp = await fetch(`${AGENT_URL}/.well-known/agent-card.json`);
    const agentCard = await cardResp.json();

    const extensions = [];
    if (agentCard.capabilities && agentCard.capabilities.extensions) {
      for (const ext of agentCard.capabilities.extensions) {
        if (ext.uri && ext.uri.includes('a2ui')) {
          extensions.push(ext);
        }
      }
    }

    const body = {
      jsonrpc: '2.0',
      id: crypto.randomUUID(),
      method: 'message/send',
      params: {
        message: {
          role: 'user',
          parts: parts,
          messageId: crypto.randomUUID(),
        },
        configuration: {
          extensions: extensions,
        },
      },
    };

    if (taskContextId) {
      body.params.message.contextId = taskContextId;
    }

    const resp = await fetch(`${AGENT_URL}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-A2A-Extensions': A2UI_EXTENSION_URI,
      },
      body: JSON.stringify(body),
    });

    const result = await resp.json();
    hideLoading();

    if (result.error) {
      appendToChatFlow('error', result.error.message || 'Agent returned an error');
      return;
    }

    const task = result.result;
    if (task && task.contextId) {
      taskContextId = task.contextId;
    }

    const a2uiMessages = [];
    const textMessages = [];

    function extractParts(msg) {
      if (msg.role !== 'agent') return;
      for (const part of msg.parts || []) {
        if (part.kind === 'data' && part.data) {
          if (
            part.data.version === 'v0.9' ||
            part.data.createSurface ||
            part.data.updateComponents ||
            part.data.updateDataModel
          ) {
            a2uiMessages.push(part.data);
          }
        } else if (part.kind === 'text' && part.text) {
          textMessages.push(part.text);
        }
      }
    }

    // Only extract from the status message (latest response).
    // History contains ALL previous messages which would duplicate old surfaces.
    if (task && task.status && task.status.message) {
      extractParts(task.status.message);
    }

    // If status message had no parts, check the last agent message in history
    if (a2uiMessages.length === 0 && textMessages.length === 0 && task && task.history) {
      const agentMsgs = task.history.filter(m => m.role === 'agent');
      if (agentMsgs.length > 0) {
        extractParts(agentMsgs[agentMsgs.length - 1]);
      }
    }

    if (a2uiMessages.length > 0) {
      appendA2UIResponse(a2uiMessages);
    } else if (textMessages.length > 0) {
      appendToChatFlow('agent', textMessages.join('\n'));
    } else {
      appendToChatFlow('agent', 'No response from agent.');
    }
  } catch (err) {
    hideLoading();
    console.error('Error:', err);
    appendToChatFlow('error', 'Failed to reach agent: ' + err.message);
  } finally {
    requesting = false;
    document.getElementById('send-btn').disabled = false;
  }
}

function appendA2UIResponse(messages) {
  responseCount++;
  const containerId = 'a2ui-response-' + responseCount;

  const wrapper = document.createElement('div');
  wrapper.className = 'agent-message';

  const container = document.createElement('div');
  container.id = containerId;
  container.className = 'a2ui-response';
  wrapper.appendChild(container);

  document.getElementById('chat-flow').appendChild(wrapper);

  const renderer = new A2UIRenderer(containerId);
  renderer.onAction = (actionName, context) => {
    console.log('A2UI Action:', actionName, context);
    sendActionToAgent(actionName, context);
  };
  renderer.processMessages(messages);

  scrollToBottom();
}

function appendToChatFlow(type, text) {
  const chatFlow = document.getElementById('chat-flow');
  const div = document.createElement('div');

  if (type === 'user') {
    div.className = 'user-message';
  } else if (type === 'error') {
    div.className = 'agent-message';
    div.style.color = '#c62828';
  } else {
    div.className = 'agent-message a2ui-card';
  }

  div.textContent = text;
  chatFlow.appendChild(div);
  scrollToBottom();
}

function hideWelcome() {
  const el = document.getElementById('welcome');
  if (el) el.style.display = 'none';
}

function showLoading() {
  hideLoading();
  const chatFlow = document.getElementById('chat-flow');
  const div = document.createElement('div');
  div.id = 'loading';
  div.className = 'loading';

  const dots = document.createElement('span');
  dots.className = 'dots';
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('span');
    dot.textContent = '.';
    dots.appendChild(dot);
  }
  div.appendChild(dots);

  const label = document.createTextNode(' Thinking...');
  div.appendChild(label);

  chatFlow.appendChild(div);
  scrollToBottom();
}

function hideLoading() {
  const el = document.getElementById('loading');
  if (el) el.remove();
}

function scrollToBottom() {
  const chatArea = document.getElementById('chat-area');
  chatArea.scrollTop = chatArea.scrollHeight;
}

function toggleDebug() {
  document.getElementById('debug-panel').classList.toggle('hidden');
}
