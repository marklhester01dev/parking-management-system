// Theme: follows the system setting until the switch in the sidebar is used; the choice is
// then remembered. Loaded in <head> so the right theme is set before the page paints.
// Convenience only: without it the page simply stays light.
(() => {
  const KEY = "parking-theme";
  const root = document.documentElement;
  const system = window.matchMedia("(prefers-color-scheme: dark)");

  const saved = () => {
    try {
      const value = localStorage.getItem(KEY);
      return value === "light" || value === "dark" ? value : null;
    } catch {
      return null;
    }
  };
  const save = (value) => {
    try {
      localStorage.setItem(KEY, value);
    } catch {
      /* storage unavailable */
    }
  };
  const preferred = () => saved() || (system.matches ? "dark" : "light");

  function apply(theme) {
    root.dataset.theme = theme;
    const toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) toggle.setAttribute("aria-checked", String(theme === "dark"));
  }

  apply(preferred());
  system.addEventListener("change", () => {
    if (!saved()) apply(preferred());
  });

  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) return;
    apply(root.dataset.theme);
    toggle.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      save(next);
      apply(next);
    });
  });
})();
