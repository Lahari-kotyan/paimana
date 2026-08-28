/**
 * PAIMANA AI Assistant & Executive Brief Generator
 */

const AssistantEngine = {
  init() {
    this.attachListeners();
  },

  attachListeners() {
    const btnSend = document.getElementById('btn-send-chat');
    const input = document.getElementById('chat-input-text');

    if (btnSend && input) {
      btnSend.addEventListener('click', () => this.sendMessage());
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') this.sendMessage();
      });
    }

    // Quick prompt chips
    document.querySelectorAll('.prompt-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const text = chip.innerText;
        document.getElementById('chat-input-text').value = text;
        this.sendMessage();
      });
    });
  },

  async sendMessage() {
    const input = document.getElementById('chat-input-text');
    const text = input.value.trim();
    if (!text) return;

    this.appendMessage('user', text);
    input.value = '';

    // Typing indicator
    const typingId = this.appendTypingIndicator();

    try {
      const res = await fetch('/api/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });
      const data = await res.json();
      this.removeTypingIndicator(typingId);
      this.appendMessage('assistant', data.response);
    } catch (err) {
      this.removeTypingIndicator(typingId);
      this.appendMessage('assistant', '⚠️ Unable to process query. Error: ' + err.message);
    }
  },

  appendMessage(sender, content) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    const div = document.createElement('div');
    div.className = `message-bubble ${sender}`;
    
    // Format simple markdown into HTML
    let formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; color: #38BDF8;">$1</code>')
      .replace(/### (.*)/g, '<h4 style="color: #38BDF8; margin: 12px 0 6px 0; font-family: Outfit, sans-serif;">$1</h4>')
      .replace(/> (.*)/g, '<blockquote style="border-left: 3px solid #0EA5E9; padding-left: 12px; margin: 8px 0; color: #94A3B8; background: rgba(14,165,233,0.06); padding: 8px 12px; border-radius: 4px;">$1</blockquote>')
      .replace(/\n/g, '<br/>');

    div.innerHTML = formatted;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  },

  appendTypingIndicator() {
    const container = document.getElementById('chat-messages-container');
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message-bubble assistant';
    div.innerHTML = `<em>PAIMANA AI is analyzing 1,981 infrastructure projects...</em>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
  },

  removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  },

  async loadProjectBrief(projectId) {
    try {
      const res = await fetch(`/api/chat/brief/${projectId}`);
      const data = await res.json();
      
      const modal = document.getElementById('brief-modal');
      const textEl = document.getElementById('brief-memo-text');
      if (modal && textEl) {
        textEl.innerText = data.brief_text;
        modal.classList.add('active');
      }
    } catch (err) {
      alert('Failed to generate briefing memo: ' + err.message);
    }
  }
};
