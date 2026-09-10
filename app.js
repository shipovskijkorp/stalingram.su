const appShell = document.querySelector('.app-shell');
const chatRows = [...document.querySelectorAll('.chat-row')];
const headerName = document.getElementById('headerName');
const headerStatus = document.getElementById('headerStatus');
const headerAvatar = document.getElementById('headerAvatar');
const chatSearch = document.getElementById('chatSearch');
const messageInput = document.getElementById('messageInput');
const composer = document.getElementById('composer');
const messageFlow = document.getElementById('messageFlow');
const messageStage = document.getElementById('messageStage');
const toast = document.getElementById('toast');
const mobileBack = document.getElementById('mobileBack');
const easterStar = document.getElementById('easterStar');

function selectChat(row) {
  chatRows.forEach((item) => item.classList.toggle('is-active', item === row));
  headerName.textContent = row.dataset.name;
  headerStatus.textContent = row.dataset.status;
  headerAvatar.textContent = row.dataset.avatar;
  appShell.classList.add('chat-open');
}

chatRows.forEach((row) => {
  row.addEventListener('click', () => selectChat(row));
});

mobileBack.addEventListener('click', () => {
  appShell.classList.remove('chat-open');
});

chatSearch.addEventListener('input', () => {
  const query = chatSearch.value.trim().toLowerCase();
  chatRows.forEach((row) => {
    row.hidden = !row.dataset.name.toLowerCase().includes(query);
  });
});

document.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    chatSearch.focus();
  }
});

messageInput.addEventListener('input', () => {
  messageInput.style.height = 'auto';
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 120)}px`;
});

messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    composer.requestSubmit();
  }
});

composer.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;

  const article = document.createElement('article');
  article.className = 'message message--outgoing';

  const paragraph = document.createElement('p');
  paragraph.textContent = text;

  const footer = document.createElement('footer');
  const now = new Date();
  const time = document.createElement('time');
  time.textContent = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  const checks = document.createElement('span');
  checks.className = 'message-check';
  checks.textContent = '✓';

  footer.append(time, checks);
  article.append(paragraph, footer);
  messageFlow.appendChild(article);

  messageInput.value = '';
  messageInput.style.height = 'auto';
  messageStage.scrollTop = messageStage.scrollHeight;

  setTimeout(() => {
    checks.textContent = '✓✓';
  }, 650);
});

let toastTimeout;
function showToast(text) {
  clearTimeout(toastTimeout);
  toast.textContent = text;
  toast.classList.add('is-visible');
  toastTimeout = setTimeout(() => toast.classList.remove('is-visible'), 2200);
}

easterStar.addEventListener('click', () => {
  const messages = [
    'Одобрено Госпланом ★',
    'Производительность интерфейса повышена на 146%',
    'Дефицита сообщений не обнаружено',
    'Товарищ, ваш онлайн учтён статистикой',
    'Серверный пятилетний план выполняется досрочно'
  ];
  showToast(messages[Math.floor(Math.random() * messages.length)]);
});

messageStage.scrollTop = messageStage.scrollHeight;
