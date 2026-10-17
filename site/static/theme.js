/* Light and dark themes (my decision of 18 October 2026).

   The page follows the system setting until a visitor chooses a theme with the switch in the
   header.
   The choice is kept in the browser under the one key "theme", the only thing any script on this
   site stores, and set on the root element as data-theme. This file loads in the head without
   defer, so a saved choice applies before the page is drawn. The switch is hidden in the markup
   and shown here, so a page without the script has no control that does nothing. */
(function () {
  "use strict";

  var root = document.documentElement;
  var saved = null;
  try {
    saved = localStorage.getItem("theme");
  } catch (error) {
    saved = null;
  }
  if (saved === "light" || saved === "dark") {
    root.setAttribute("data-theme", saved);
  }

  function isDark() {
    var chosen = root.getAttribute("data-theme");
    if (chosen) {
      return chosen === "dark";
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var button = document.querySelector(".theme-switch");
    if (!button) {
      return;
    }
    button.setAttribute("aria-pressed", isDark() ? "true" : "false");
    button.hidden = false;
    button.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      button.setAttribute("aria-pressed", next === "dark" ? "true" : "false");
      try {
        localStorage.setItem("theme", next);
      } catch (error) {
        // Storage can be refused (a private window, for example); the theme still applies to
        // this page.
        return;
      }
    });
  });
})();
