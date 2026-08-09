const form = document.querySelector('#chat-form');
const input = document.querySelector('#message');
const messages = document.querySelector('#messages');
const emptyState = document.querySelector('#empty-state');
const sendButton = document.querySelector('#send-button');
const status = document.querySelector('#connection-status');
let conversationId = null;

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
  content.textContent = text;
  article.append(content);
  if (role === 'assistant') article.append(copyButton(text));
  messages.append(article);
  article.scrollIntoView({ block: 'end', behavior: 'smooth' });
  return article;
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
  const message = input.value.trim();
  if (!message || sendButton.disabled) return;
  appendMessage('user', message);
  input.value = '';
  resizeComposer();
  sendButton.disabled = true;
  setStatus('Replying…', true);
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
    const body = await responseBody(response);
    if (!response.ok) throw new Error(body.error?.message || 'The request could not be completed.');
    conversationId = body.conversation_id;
    appendMessage('assistant', body.message);
    setStatus('Ready');
  } catch (error) {
    appendMessage('error', `${error.message} Try again when you are ready.`);
    setStatus('Could not reply');
  } finally {
    sendButton.disabled = false;
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
  input.focus();
});
