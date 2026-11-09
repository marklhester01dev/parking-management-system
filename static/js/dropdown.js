// Dropdown: replaces the look of a native <select> (select_field macro in _macros.html) with a
// styled button and list. The native <select> stays in the page, visually hidden, and is the
// field that is validated and submitted; this file only mirrors its value both ways.
// Keyboard: Enter/Space/Arrow open, Arrows/Home/End move, Enter picks, Esc and Tab close,
// typing a letter jumps to the matching option.
// Convenience only: without it the native select is shown and works as before.
(() => {
  document.querySelectorAll("[data-select]").forEach(init);

  function init(root) {
    const select = root.querySelector("select");
    const trigger = root.querySelector("[data-select-trigger]");
    const menu = root.querySelector("[data-select-menu]");
    const text = root.querySelector("[data-select-label]");
    if (!select || !trigger || !menu || !text) return;

    // A required field has no empty choice in the list (the placeholder is only the label).
    const options = [...menu.querySelectorAll('[role="option"]')].filter(
      (option) => {
        if (select.required && option.dataset.value === "") {
          option.remove();
          return false;
        }
        return true;
      },
    );
    let active = -1;
    let typed = "";
    let typedTimer = null;

    root.dataset.enhanced = "";

    const isOpen = () => !menu.hidden;
    const selectedIndex = () =>
      options.findIndex((o) => o.dataset.value === select.value);

    function sync() {
      const chosen = select.options[select.selectedIndex];
      text.textContent = chosen ? chosen.text : "";
      if (select.value === "") text.setAttribute("data-empty", "");
      else text.removeAttribute("data-empty");
      options.forEach((o) =>
        o.setAttribute(
          "aria-selected",
          String(o.dataset.value === select.value),
        ),
      );
    }

    function setActive(index) {
      options.forEach((o) => o.removeAttribute("data-active"));
      active = index;
      if (index < 0 || !options[index]) {
        trigger.removeAttribute("aria-activedescendant");
        return;
      }
      options[index].setAttribute("data-active", "");
      trigger.setAttribute("aria-activedescendant", options[index].id);
      options[index].scrollIntoView({ block: "nearest" });
    }

    function open() {
      if (trigger.disabled || isOpen() || !options.length) return;
      // Close any other open dropdown first.
      document
        .querySelectorAll("[data-select-trigger][aria-expanded=true]")
        .forEach((t) => {
          if (t !== trigger) t.dispatchEvent(new Event("select:close"));
        });
      menu.hidden = false;
      // Open upward when there is no room below and more room above.
      const box = trigger.getBoundingClientRect();
      const below = window.innerHeight - box.bottom;
      const needed = menu.offsetHeight + 8;
      menu.dataset.placement =
        below < needed && box.top > below ? "top" : "bottom";
      trigger.setAttribute("aria-expanded", "true");
      const current = selectedIndex();
      setActive(current >= 0 ? current : 0);
    }

    function close() {
      if (!isOpen()) return;
      menu.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      setActive(-1);
    }

    function choose(index) {
      const option = options[index];
      if (!option) return;
      if (select.value !== option.dataset.value) {
        select.value = option.dataset.value;
        select.dispatchEvent(new Event("input", { bubbles: true }));
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
      trigger.classList.remove("is-invalid");
      sync();
      close();
      trigger.focus();
    }

    trigger.addEventListener("click", () => (isOpen() ? close() : open()));
    trigger.addEventListener("select:close", close);

    trigger.addEventListener("keydown", (event) => {
      const last = options.length - 1;
      switch (event.key) {
        case "ArrowDown":
          event.preventDefault();
          if (!isOpen()) open();
          else setActive(Math.min(active + 1, last));
          break;
        case "ArrowUp":
          event.preventDefault();
          if (!isOpen()) open();
          else setActive(Math.max(active - 1, 0));
          break;
        case "Home":
          if (isOpen()) {
            event.preventDefault();
            setActive(0);
          }
          break;
        case "End":
          if (isOpen()) {
            event.preventDefault();
            setActive(last);
          }
          break;
        case "Enter":
        case " ":
          event.preventDefault();
          if (isOpen()) choose(active);
          else open();
          break;
        case "Escape":
          if (isOpen()) {
            event.preventDefault();
            event.stopPropagation();
            close();
          }
          break;
        case "Tab":
          close();
          break;
        default:
          if (
            event.key.length === 1 &&
            !event.ctrlKey &&
            !event.metaKey &&
            !event.altKey
          ) {
            typed += event.key.toLowerCase();
            clearTimeout(typedTimer);
            typedTimer = setTimeout(() => {
              typed = "";
            }, 600);
            const from = isOpen() ? active : selectedIndex();
            const ordered = options
              .slice(from + 1)
              .concat(options.slice(0, from + 1));
            const hit = ordered.find((o) =>
              o.textContent.trim().toLowerCase().startsWith(typed),
            );
            if (hit) {
              const index = options.indexOf(hit);
              if (isOpen()) setActive(index);
              else choose(index);
            }
          }
      }
    });

    options.forEach((option, index) => {
      // mousedown would move focus off the button; keep it there.
      option.addEventListener("mousedown", (event) => event.preventDefault());
      option.addEventListener("mousemove", () => {
        if (active !== index) setActive(index);
      });
      option.addEventListener("click", () => choose(index));
    });

    document.addEventListener("click", (event) => {
      if (!root.contains(event.target)) close();
    });
    window.addEventListener("resize", close);

    // Clicking the label focuses the button (the native select is hidden).
    const label = document.querySelector(`label[for="${select.id}"]`);
    if (label)
      label.addEventListener("click", (event) => {
        event.preventDefault();
        trigger.focus();
      });

    // Failed native validation (required, empty): mark and focus the visible button.
    select.addEventListener("invalid", () => {
      trigger.classList.add("is-invalid");
      trigger.focus();
    });
    select.addEventListener("change", sync);
    if (select.form)
      select.form.addEventListener("reset", () => setTimeout(sync));
    sync();
  }
})();
