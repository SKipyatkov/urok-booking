/** Urok Booking — shared UI behaviors */

(function () {
  "use strict";

  function showToast(message, type) {
    var container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.className = "toast-container";
      container.setAttribute("aria-live", "polite");
      document.body.appendChild(container);
    }
    var toast = document.createElement("div");
    toast.className = "toast toast--" + (type || "success");
    toast.textContent = message;
    container.appendChild(toast);
    requestAnimationFrame(function () {
      toast.classList.add("toast--visible");
    });
    setTimeout(function () {
      toast.classList.remove("toast--visible");
      setTimeout(function () {
        toast.remove();
      }, 300);
    }, 2600);
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    e.preventDefault();
    var targetId = btn.getAttribute("data-copy");
    var input = targetId ? document.getElementById(targetId) : null;
    var text = input ? input.value : btn.getAttribute("data-copy-text");
    if (!text) return;
    navigator.clipboard.writeText(text).then(function () {
      var label = btn.getAttribute("data-copy-label") || "Скопировано";
      showToast(label, "success");
      btn.classList.add("btn-copied");
      setTimeout(function () {
        btn.classList.remove("btn-copied");
      }, 1200);
    });
  });

  function bindSlotSelection() {
    var container = document.getElementById("slots-container");
    if (!container) return;

    container.addEventListener("change", function (e) {
      if (e.target.name !== "slot_radio") return;
      var hidden = document.getElementById("slot_start");
      var submit = document.getElementById("submit-btn");
      var preview = document.getElementById("slot-preview");
      if (hidden) hidden.value = e.target.value;
      if (submit) submit.disabled = false;
      if (preview) {
        var label = e.target.closest(".slot-btn");
        label = label ? label.querySelector("label") : null;
        preview.hidden = false;
        preview.querySelector(".slot-preview__time").textContent = label
          ? label.textContent.trim()
          : "";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      bindSlotSelection();
      restoreSlotSubmit();
    });
  } else {
    bindSlotSelection();
    restoreSlotSubmit();
  }

  function restoreSlotSubmit() {
    var hidden = document.getElementById("slot_start");
    var submit = document.getElementById("submit-btn");
    if (hidden && submit && hidden.value) {
      submit.disabled = false;
    }
  }

  document.body.addEventListener("htmx:afterSwap", function (e) {
    if (e.detail.target && e.detail.target.id === "slots-container") {
      var hidden = document.getElementById("slot_start");
      var submit = document.getElementById("submit-btn");
      var preview = document.getElementById("slot-preview");
      if (hidden) hidden.value = "";
      if (submit) submit.disabled = true;
      if (preview) preview.hidden = true;
    }
  });
})();
