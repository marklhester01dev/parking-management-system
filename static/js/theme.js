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

  // The sidebar button draws its label, icon and switch from <html data-theme>, so nothing
  // else has to be updated here.
  const apply = (theme) => {
    root.dataset.theme = theme;
  };

  apply(preferred());
  system.addEventListener("change", () => {
    if (!saved()) apply(preferred());
  });

  document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) return;
    toggle.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      save(next);
      apply(next);
    });
  });
})();
