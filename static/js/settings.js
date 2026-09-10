const themeOptions = [...document.querySelectorAll("[data-theme-option]")];
const themeColorMeta = document.querySelector('meta[name="theme-color"]');
const enterToggle = document.getElementById("id_enter_to_send");
const enterModeHint = document.getElementById("enterModeHint");

function previewTheme(theme) {
  document.body.dataset.theme = theme;
  themeOptions.forEach((option) => {
    option.classList.toggle("is-selected", option.dataset.themeOption === theme);
  });
  if (themeColorMeta) themeColorMeta.content = theme === "dark" ? "#171412" : "#801f28";
}

themeOptions.forEach((option) => {
  const radio = option.querySelector('input[type="radio"]');
  radio?.addEventListener("change", () => {
    if (radio.checked) previewTheme(radio.value);
  });
});

function updateEnterHint() {
  if (!enterToggle || !enterModeHint) return;
  enterModeHint.textContent = enterToggle.checked
    ? "Enter отправляет сообщение, Shift+Enter создаёт новую строку."
    : "Enter создаёт новую строку, Ctrl+Enter отправляет сообщение.";
}

enterToggle?.addEventListener("change", updateEnterHint);
updateEnterHint();
