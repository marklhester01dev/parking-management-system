// Sidebar: slide-in drawer under 992px. Convenience only: every link works without it.
(() => {
  const desktop = window.matchMedia("(min-width: 992px)");

  document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;
    const page = document.getElementById("page");
    const backdrop = document.querySelector("[data-nav-backdrop]");
    const closeButton = sidebar.querySelector("[data-nav-close]");
    const openButton = document.querySelector("[data-nav-open]");

    function openDrawer() {
      sidebar.dataset.open = "true";
      backdrop.dataset.open = "true";
      openButton.setAttribute("aria-expanded", "true");
      page.inert = true;
      document.body.style.overflow = "hidden";
      // The drawer turns visible as its slide starts, so focus it one frame later.
      setTimeout(() => {
        if (sidebar.dataset.open === "true") closeButton.focus();
      }, 50);
    }

    function closeDrawer(returnFocus = true) {
      if (sidebar.dataset.open !== "true") return;
      delete sidebar.dataset.open;
      delete backdrop.dataset.open;
      openButton.setAttribute("aria-expanded", "false");
      page.inert = false;
      document.body.style.overflow = "";
      if (returnFocus) openButton.focus();
    }

    openButton.addEventListener("click", openDrawer);
    closeButton.addEventListener("click", () => closeDrawer());
    backdrop.addEventListener("click", () => closeDrawer());
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeDrawer();
    });
    desktop.addEventListener("change", () => closeDrawer(false));
  });
})();
