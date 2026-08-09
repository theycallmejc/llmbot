const form = document.querySelector('#chat-form');
const input = document.querySelector('#message');
const messages = document.querySelector('#messages');
let conversationId = null;

function addMessage(role, text) {
  const element = document.createElement('p');
  element.className = role;
  element.textContent = text;
  messages.append(element);
  element.scrollIntoView({ block: 'end', behavior: 'smooth' });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  addMessage('user', message); input.value = '';
  const button = form.querySelector('button'); button.disabled = true;
  try {
    const response = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, conversation_id: conversationId }) });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || 'Request failed');
    conversationId = body.conversation_id; addMessage('assistant', body.message);
  } catch (error) { addMessage('error', error.message); }
  finally { button.disabled = false; input.focus(); }
});

document.querySelector('#new-chat').addEventListener('click', () => { conversationId = null; messages.replaceChildren(); addMessage('assistant', 'New conversation started.'); input.focus(); });

