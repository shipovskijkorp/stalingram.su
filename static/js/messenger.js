const chatFilter = document.getElementById("chatFilter");
const chatRows = [...document.querySelectorAll("[data-chat-row]")];
const chatFilterEmpty = document.getElementById("chatFilterEmpty");

if (chatFilter) {
  chatFilter.addEventListener("input", () => {
    const query = chatFilter.value.trim().toLowerCase().replace(/^@/, "");
    let visible = 0;
    chatRows.forEach((row) => {
      const matches = !query || (row.dataset.search || "").includes(query);
      row.hidden = !matches;
      if (matches) visible += 1;
    });
    if (chatFilterEmpty) chatFilterEmpty.hidden = visible !== 0 || chatRows.length === 0;
  });
}

const form = document.getElementById("messageForm");
const messageInput = document.getElementById("messageInput");
const attachmentInput = document.getElementById("attachmentsInput");
const attachmentTray = document.getElementById("attachmentTray");
const messageFlow = document.getElementById("messageFlow");
const messageStage = document.getElementById("messageStage");
const sendButton = document.getElementById("sendButton");

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}

function updateAttachmentTray() {
  if (!attachmentInput || !attachmentTray) return;
  const files = [...(attachmentInput.files || [])];
  attachmentTray.replaceChildren();
  attachmentTray.hidden = files.length === 0;
  files.forEach((file) => {
    const chip = document.createElement("span");
    chip.className = "attachment-chip";
    chip.textContent = `${file.name} · ${formatBytes(file.size)}`;
    attachmentTray.appendChild(chip);
  });
}

attachmentInput?.addEventListener("change", updateAttachmentTray);

function autoSizeInput() {
  if (!messageInput) return;
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 132)}px`;
}

messageInput?.addEventListener("input", autoSizeInput);
messageInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form?.requestSubmit();
  }
});

function nearBottom() {
  if (!messageStage) return true;
  return messageStage.scrollHeight - messageStage.scrollTop - messageStage.clientHeight < 180;
}

function scrollToBottom(force = false) {
  if (!messageStage || (!force && !nearBottom())) return;
  messageStage.scrollTop = messageStage.scrollHeight;
}

function makeMedia(attachment) {
  if (attachment.kind === "image") {
    const link = document.createElement("a");
    link.className = "message-media__item";
    link.href = attachment.url;
    link.target = "_blank";
    link.rel = "noopener";
    const image = document.createElement("img");
    image.className = "message-media__image";
    image.src = attachment.url;
    image.alt = attachment.name;
    image.loading = "lazy";
    image.addEventListener("load", () => scrollToBottom());
    link.appendChild(image);
    return link;
  }

  if (attachment.kind === "video") {
    const video = document.createElement("video");
    video.className = "message-media__video";
    video.controls = true;
    video.preload = "metadata";
    video.src = attachment.url;
    return video;
  }

  if (attachment.kind === "audio") {
    const wrapper = document.createElement("div");
    wrapper.className = "message-media__audio";
    const name = document.createElement("span");
    name.textContent = attachment.name;
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.preload = "metadata";
    audio.src = attachment.url;
    wrapper.append(name, audio);
    return wrapper;
  }

  const link = document.createElement("a");
  link.className = "message-media__file";
  link.href = attachment.url;
  link.target = "_blank";
  link.rel = "noopener";
  link.textContent = attachment.name;
  return link;
}

function renderMessage(message) {
  if (!messageFlow || document.querySelector(`[data-message-id="${message.id}"]`)) return;

  const shouldFollow = nearBottom();
  const article = document.createElement("article");
  article.className = `message ${message.is_own ? "message--outgoing" : "message--incoming"}`;
  article.dataset.messageId = String(message.id);

  if (message.attachments?.length) {
    const media = document.createElement("div");
    media.className = "message-media";
    message.attachments.forEach((attachment) => media.appendChild(makeMedia(attachment)));
    article.appendChild(media);
  }

  if (message.text) {
    const paragraph = document.createElement("p");
    paragraph.className = "message__text";
    paragraph.textContent = message.text;
    article.appendChild(paragraph);
  }

  const footer = document.createElement("footer");
  const time = document.createElement("time");
  time.textContent = message.time;
  footer.appendChild(time);
  if (message.is_own) {
    const check = document.createElement("span");
    check.className = "message-check";
    check.textContent = "✓✓";
    footer.appendChild(check);
  }
  article.appendChild(footer);
  messageFlow.appendChild(article);

  if (shouldFollow) requestAnimationFrame(() => scrollToBottom(true));
}

function formErrorText(payload) {
  const groups = Object.values(payload?.errors || {});
  const first = groups.flat()[0];
  return first?.message || "Не удалось отправить сообщение.";
}

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const hasText = Boolean(messageInput?.value.trim());
    const hasFiles = Boolean(attachmentInput?.files?.length);
    if (!hasText && !hasFiles) return;

    sendButton.disabled = true;
    const data = new FormData(form);
    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: data,
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok) throw new Error(formErrorText(payload));

      renderMessage(payload.message);
      newestMessageId = Math.max(newestMessageId, Number(payload.message.id) || 0);
      form.reset();
      updateAttachmentTray();
      if (messageInput) {
        messageInput.style.height = "auto";
        messageInput.focus();
      }
      scrollToBottom(true);
    } catch (error) {
      if (typeof showToast === "function") showToast(error.message || "Не удалось отправить сообщение.");
    } finally {
      sendButton.disabled = false;
    }
  });
}

let newestMessageId = 0;
document.querySelectorAll("[data-message-id]").forEach((node) => {
  newestMessageId = Math.max(newestMessageId, Number(node.dataset.messageId) || 0);
});

let pollBusy = false;
async function pollMessages() {
  if (!messageStage?.dataset.pollUrl || pollBusy || document.hidden) return;
  pollBusy = true;
  try {
    const url = new URL(messageStage.dataset.pollUrl, window.location.origin);
    url.searchParams.set("after", String(newestMessageId));
    const response = await fetch(url, { credentials: "same-origin" });
    if (!response.ok) return;
    const payload = await response.json();
    for (const message of payload.messages || []) {
      newestMessageId = Math.max(newestMessageId, Number(message.id) || 0);
      renderMessage(message);
    }
  } finally {
    pollBusy = false;
  }
}

if (messageStage) {
  requestAnimationFrame(() => scrollToBottom(true));
  window.setInterval(pollMessages, 2500);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) pollMessages();
  });
}
