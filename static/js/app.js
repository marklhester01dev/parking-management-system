// Convenience only: the server never relies on this.
// A form with data-confirm asks first in the modal dialog (#confirm-dialog in base.html).
// Optional on the form: data-confirm-title (heading) and data-confirm-action (button label).
// Without <dialog> support it falls back to the browser's own confirm box.
(() => {
  const dialog = document.getElementById("confirm-dialog");
  const canModal = dialog && typeof dialog.showModal === "function";
  let pending = null;

  document.addEventListener("submit", (event) => {
    const form = event.target;
    const message = form.dataset ? form.dataset.confirm : null;
    if (!message) return;

    // Second pass: the person confirmed, let the submit through.
    if (form.dataset.confirmed === "true") {
      delete form.dataset.confirmed;
      return;
    }
    event.preventDefault();

    if (!canModal) {
      if (window.confirm(message)) form.submit();
      return;
    }
    pending = { form, submitter: event.submitter };
    dialog.querySelector("[data-confirm-title]").textContent =
      form.dataset.confirmTitle || "Please confirm";
    dialog.querySelector("[data-confirm-message]").textContent = message;
    dialog.querySelector("[data-confirm-accept]").textContent =
      form.dataset.confirmAction || "Confirm";
    dialog.showModal(); // focus starts on Cancel, the safe choice
  });

  if (!canModal) return;

  dialog.addEventListener("close", () => {
    const request = pending;
    pending = null;
    const confirmed = dialog.returnValue === "confirm";
    dialog.returnValue = "";
    if (confirmed && request) {
      request.form.dataset.confirmed = "true";
      request.form.requestSubmit(request.submitter || undefined);
    }
  });

  // A click on the dimmed backdrop (the dialog element itself, outside its box) cancels.
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    const inside =
      event.clientX >= box.left &&
      event.clientX <= box.right &&
      event.clientY >= box.top &&
      event.clientY <= box.bottom;
    if (!inside) dialog.close("cancel");
  });
})();
