// Convenience only: the server never relies on this.
// A form with data-confirm asks before it submits.
document.addEventListener("submit", (event) => {
  const message = event.target.dataset ? event.target.dataset.confirm : null;
  if (message && !window.confirm(message)) {
    event.preventDefault();
  }
});
