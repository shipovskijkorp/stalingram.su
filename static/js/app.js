const toast = document.getElementById("toast");
const easterStar = document.getElementById("easterStar");
let toastTimeout;

function showToast(text) {
  if (!toast) return;
  clearTimeout(toastTimeout);
  toast.textContent = text;
  toast.classList.add("is-visible");
  toastTimeout = setTimeout(() => toast.classList.remove("is-visible"), 2200);
}

if (easterStar) {
  easterStar.addEventListener("click", () => {
    const messages = [
      "Одобрено Госпланом ★",
      "Производительность интерфейса повышена на 146%",
      "Дефицита сообщений не обнаружено",
      "Товарищ, ваш онлайн учтён статистикой",
      "Пятилетний план по регистрации выполняется досрочно"
    ];
    showToast(messages[Math.floor(Math.random() * messages.length)]);
  });
}
