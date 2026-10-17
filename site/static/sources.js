/* Sourced figures (task P5-06).

   Every figure marked with a.source-mark links to its entry in the list of sources at the end of
   the page, so the page reads and the link works without this script. With the script, a click,
   tap or Enter opens the entry in a popover next to the figure. Escape, the Close button or a tap
   elsewhere dismisses it. The script reads the page and changes it; it makes no request. */
(function () {
  "use strict";

  var popover = document.getElementById("source-popover");
  if (!popover) {
    return;
  }
  var nameField = popover.querySelector(".source-popover-name");
  var fields = {
    document: popover.querySelector('[data-field="document"]'),
    page: popover.querySelector('[data-field="page"]'),
    date: popover.querySelector('[data-field="date"]')
  };
  var moreLink = popover.querySelector(".source-popover-link");
  var closeButton = popover.querySelector(".source-popover-close");
  var opener = null;
  var widthWhenOpened = 0;
  var openedAt = { left: 0, top: 0 };

  // Where the figure is on the page, whatever the scroll position.
  function figurePosition() {
    var box = opener.getBoundingClientRect();
    return { left: box.left + window.pageXOffset, top: box.top + window.pageYOffset };
  }

  function figureMoved() {
    var now = figurePosition();
    return Math.abs(now.left - openedAt.left) > 1 || Math.abs(now.top - openedAt.top) > 1;
  }

  // Spacing comes from the design tokens, so the script holds no size of its own.
  function space(name) {
    var root = document.documentElement;
    var rootSize = parseFloat(getComputedStyle(root).fontSize);
    return parseFloat(getComputedStyle(root).getPropertyValue(name)) * rootSize;
  }

  function entryText(entry, part) {
    var node = entry.querySelector(".ref-" + part);
    return node ? node.textContent : "";
  }

  function fill(entry) {
    nameField.textContent = entryText(entry, "name");
    fields.document.textContent = entryText(entry, "source");
    fields.page.textContent = entryText(entry, "location");
    fields.date.textContent = entryText(entry, "date");
    var more = entry.querySelector(".ref-link");
    if (more) {
      moreLink.setAttribute("href", more.getAttribute("href"));
      moreLink.textContent = more.textContent;
      moreLink.hidden = false;
    } else {
      moreLink.removeAttribute("href");
      moreLink.hidden = true;
    }
  }

  function place() {
    var gap = space("--space-2");
    var box = opener.getBoundingClientRect();
    var scrollX = window.pageXOffset;
    var scrollY = window.pageYOffset;
    var farLeft = scrollX + gap;
    var farRight = scrollX + document.documentElement.clientWidth - popover.offsetWidth - gap;
    var left = Math.max(farLeft, Math.min(scrollX + box.left, farRight));
    var top = scrollY + box.bottom + gap;
    var fitsBelow = box.bottom + gap + popover.offsetHeight <= window.innerHeight;
    var fitsAbove = box.top - gap - popover.offsetHeight >= 0;
    if (!fitsBelow && fitsAbove) {
      top = scrollY + box.top - gap - popover.offsetHeight;
    }
    popover.style.left = left + "px";
    popover.style.top = top + "px";
  }

  function openPopover(mark) {
    var entry = document.getElementById(mark.getAttribute("href").slice(1));
    if (!entry) {
      return false;
    }
    if (opener) {
      opener.setAttribute("aria-expanded", "false");
    }
    fill(entry);
    opener = mark;
    widthWhenOpened = window.innerWidth;
    openedAt = figurePosition();
    mark.setAttribute("aria-expanded", "true");
    popover.hidden = false;
    place();
    popover.focus({ preventScroll: true });
    return true;
  }

  function closePopover(returnFocus) {
    if (!opener) {
      return;
    }
    var mark = opener;
    opener = null;
    mark.setAttribute("aria-expanded", "false");
    popover.hidden = true;
    if (returnFocus) {
      mark.focus();
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll("a.source-mark"), function (mark) {
    mark.setAttribute("aria-expanded", "false");
    mark.setAttribute("aria-controls", "source-popover");
    mark.addEventListener("click", function (event) {
      if (opener === mark) {
        event.preventDefault();
        closePopover(true);
      } else if (openPopover(mark)) {
        event.preventDefault();
      }
    });
  });

  closeButton.addEventListener("click", function () {
    closePopover(true);
  });

  // Tab leaves the popover to the figure it came from, so a keyboard user keeps their place.
  function keepTabInside(event) {
    var first = moreLink.hidden ? closeButton : moreLink;
    var active = document.activeElement;
    var leavingBackwards = event.shiftKey && (active === popover || active === first);
    var leavingForwards = !event.shiftKey && active === closeButton;
    if (leavingBackwards || leavingForwards) {
      event.preventDefault();
      closePopover(true);
    }
  }

  document.addEventListener("keydown", function (event) {
    if (!opener) {
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      closePopover(true);
    } else if (event.key === "Tab" && popover.contains(document.activeElement)) {
      keepTabInside(event);
    }
  });

  document.addEventListener("pointerdown", function (event) {
    if (opener && !popover.contains(event.target) && !opener.contains(event.target)) {
      closePopover(false);
    }
  });

  // The popover is placed once, in page coordinates, so scrolling the page keeps it beside its
  // figure. It would be left behind if the figure moved, for example when a table scrolls
  // sideways or the width changes. A phone's address bar changes the height on every scroll,
  // which is not a reason to close.
  document.addEventListener(
    "scroll",
    function () {
      if (opener && figureMoved()) {
        closePopover(false);
      }
    },
    true
  );
  window.addEventListener("resize", function () {
    if (window.innerWidth !== widthWhenOpened) {
      closePopover(false);
    }
  });
})();
