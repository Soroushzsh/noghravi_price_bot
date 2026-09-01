document.addEventListener("DOMContentLoaded", () => {
  const button = document.querySelector("[data-theme-toggle]");
  if (button) {
    button.setAttribute("aria-pressed", document.documentElement.dataset.theme === "dark");
    button.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    button.setAttribute("aria-pressed", next === "dark");
    try { localStorage.setItem("theme", next); } catch (_) {}
  });
  }
});
