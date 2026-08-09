const form = document.querySelector('#chat-form');
const input = document.querySelector('#message');
const messages = document.querySelector('#messages');
const emptyState = document.querySelector('#empty-state');
const sendButton = document.querySelector('#send-button');
const status = document.querySelector('#connection-status');
let conversationId = null;
let activeRequest = null;

async function refreshConversations() {
  const response = await fetch('/api/conversations');
  if (!response.ok) return;
  const list = await response.json();
  const nav = document.querySelector('#conversation-list');
  nav.replaceChildren();
  list.forEach((item) => {
    const button = document.createElement('button');
    button.type = 'button'; button.textContent = item.title; button.className = 'conversation-link';
    button.classList.toggle('is-current', item.id === conversationId);
    button.addEventListener('click', () => loadConversation(item.id));
    nav.append(button);
  });
}

async function loadConversation(id) {
  const response = await fetch(`/api/conversations/${encodeURIComponent(id)}`);
  if (!response.ok) return;
  const item = await response.json(); conversationId = item.id;
  messages.replaceChildren();
  item.messages.forEach((message) => appendMessage(message.role, message.content));
  document.querySelector('h1').textContent = item.title;
  setStatus('Ready'); refreshConversations();
}

function setStatus(text, busy = false) {
  status.textContent = text;
  status.classList.toggle('is-busy', busy);
}

function copyButton(text) {
  const button = document.createElement('button');
  button.className = 'message-action';
  button.type = 'button';
  button.textContent = 'Copy';
  button.addEventListener('click', async () => {
    await navigator.clipboard.writeText(text);
    button.textContent = 'Copied';
    window.setTimeout(() => { button.textContent = 'Copy'; }, 1200);
  });
  return button;
}

function appendMessage(role, text) {
  emptyState?.remove();
  const article = document.createElement('article');
  article.className = `message ${role}`;
  const content = document.createElement('div');
  content.className = 'message-content';
  renderMarkdown(content, text);
  article.append(content);
  if (role === 'assistant') article.append(copyButton(text));
  messages.append(article);
  article.scrollIntoView({ block: 'end', behavior: 'smooth' });
  return article;
}

function inlineMarkdown(target, text) {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  for (const part of parts) {
    if (part.startsWith('`') && part.endsWith('`')) {
      const code = document.createElement('code'); code.textContent = part.slice(1, -1); target.append(code);
    } else if (part.startsWith('**') && part.endsWith('**')) {
      const strong = document.createElement('strong'); strong.textContent = part.slice(2, -2); target.append(strong);
    } else { target.append(document.createTextNode(part)); }
  }
}

function renderMarkdown(target, text) {
  const chunks = text.split(/```([\s\S]*?)```/g);
  chunks.forEach((chunk, index) => {
    if (index % 2) {
      const pre = document.createElement('pre'); const code = document.createElement('code');
      code.textContent = chunk.replace(/^\w*\n?/, ''); pre.append(code); target.append(pre);
      return;
    }
    chunk.split('\n').forEach((line) => {
      const paragraph = document.createElement('p');
      const heading = line.match(/^(#{1,3})\s+(.+)$/);
      if (heading) { const title = document.createElement(`h${heading[1].length + 2}`); inlineMarkdown(title, heading[2]); target.append(title); }
      else { inlineMarkdown(paragraph, line); target.append(paragraph); }
    });
  });
}

async function responseBody(response) {
  const raw = await response.text();
  try { return JSON.parse(raw); }
  catch { return { error: { message: raw || `Request failed (${response.status})` } }; }
}

function resizeComposer() {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
}

async function sendMessage() {
  if (activeRequest) { activeRequest.abort(); return; }
  const message = input.value.trim();
  if (!message || sendButton.disabled) return;
  appendMessage('user', message);
  input.value = '';
  resizeComposer();
  sendButton.disabled = true;
  sendButton.disabled = false; sendButton.textContent = 'Stop';
  activeRequest = new AbortController();
  setStatus('Replying…', true);
  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: conversationId }), signal: activeRequest.signal,
    });
    if (!response.ok) { const body = await responseBody(response); throw new Error(body.error?.message || 'The request could not be completed.'); }
    const assistant = appendMessage('assistant', ''); const content = assistant.querySelector('.message-content');
    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = ''; let text = '';
    while (true) {
      const { value, done } = await reader.read(); if (done) break;
      buffer += decoder.decode(value, { stream: true }); const events = buffer.split('\n\n'); buffer = events.pop();
      for (const event of events) {
        const type = event.match(/event: (.+)/)?.[1]; const data = event.match(/data: (.+)/)?.[1]; if (!data) continue;
        const payload = JSON.parse(data); if (type === 'chunk') { text += payload.text; renderMarkdown(content, text); }
        if (type === 'done') conversationId = payload.conversation_id;
        if (type === 'error') throw new Error(payload.message);
      }
    }
    document.querySelector('h1').textContent = message.split(/\s+/).slice(0, 8).join(' ') || 'New conversation';
    refreshConversations();
    setStatus('Ready');
  } catch (error) {
    if (error.name === 'AbortError') { setStatus('Generation stopped'); return; }
    appendMessage('error', `${error.message} Try again when you are ready.`);
    setStatus('Could not reply');
  } finally {
    activeRequest = null; sendButton.disabled = false; sendButton.innerHTML = 'Send <span aria-hidden="true">↵</span>';
    input.focus();
  }
}

form.addEventListener('submit', (event) => { event.preventDefault(); sendMessage(); });
input.addEventListener('input', resizeComposer);
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); sendMessage(); }
});
document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => {
  input.value = button.dataset.prompt;
  resizeComposer();
  input.focus();
}));
document.querySelector('#new-chat').addEventListener('click', () => {
  conversationId = null;
  messages.replaceChildren(emptyState || document.createElement('div'));
  if (!emptyState) window.location.reload();
  setStatus('Ready');
  document.querySelector('h1').textContent = 'New conversation';
  input.focus();
});

refreshConversations();
