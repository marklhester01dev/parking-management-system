// Toast notifications (flashed messages): they are already in the page, fixed at the top of the
// screen. This only closes them: after a few seconds (errors stay longer), or at once with the
// close button. The timer pauses while the pointer or keyboard focus is on a toast.
// Convenience only: without it the toasts simply stay until the next page.
(() => {
  const DELAY = { danger: 8000, warning: 8000 };
  const DEFAULT_DELAY = 5000;
  const LEAVE_MS = 250;

  document.querySelectorAll("[data-toast]").forEach((toast) => {
    let timer = null;
    let remaining = DELAY[toast.dataset.tone] || DEFAULT_DELAY;
    let startedAt = 0;

    const dismiss = () => {
      clearTimeout(timer);
      if (toast.dataset.leaving !== undefined) return;
      toast.dataset.leaving = "";
      setTimeout(() => {
        const stack = toast.parentElement;
        toast.remove();
        if (stack && !stack.children.length) stack.remove();
      }, LEAVE_MS);
    };
    const start = () => {
      clearTimeout(timer);
      startedAt = Date.now();
      timer = setTimeout(dismiss, remaining);
    };
    const pause = () => {
      clearTimeout(timer);
      remaining = Math.max(1500, remaining - (Date.now() - startedAt));
    };

    toast.addEventListener("mouseenter", pause);
    toast.addEventListener("mouseleave", start);
    toast.addEventListener("focusin", pause);
    toast.addEventListener("focusout", start);
    const close = toast.querySelector("[data-toast-close]");
    if (close) close.addEventListener("click", dismiss);
    start();
  });
})();
