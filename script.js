/* TONFTP LLC marketing site — script.js
   Purpose: (1) shared footer, single source of truth; (2) reveal-on-scroll
   via IntersectionObserver with stagger. Zero dependencies. Without JS the
   .no-js class keeps everything visible (progressive enhancement). */

document.documentElement.classList.remove("no-js");

/* Shared footer — edit FOOTER_NOTE here and every page picks it up; each
   page carries only an empty <footer class="footer" data-footer></footer>
   placeholder. The year is computed at runtime so it never goes stale. */
(function renderFooter() {
  const FOOTER_NOTE =
    "tonftp.com is owned and operated by TONFTP LLC.";

  const footer = document.querySelector("footer.footer[data-footer]");
  if (!footer) return;

  footer.innerHTML =
    '<div class="container footer-inner">' +
    '<div class="footer-brand">' +
    '<img src="assets/icon.png" alt="" width="24" height="24" /> TON<b>FTP</b>' +
    "</div>" +
    '<nav aria-label="Footer">' +
    '<a href="#services">What we do</a>' +
    '<a href="#process">How we work</a>' +
    '<a href="#work">Work</a>' +
    '<a href="#about">Company</a>' +
    '<a href="mailto:hello@tonftp.com">Contact</a>' +
    "</nav>" +
    `<small>© ${new Date().getFullYear()} TONFTP LLC · ${FOOTER_NOTE}</small>` +
    "</div>";
})();

(function () {
  let els = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    els.forEach(function (el) {
      el.classList.add("visible");
    });
    return;
  }

  const io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" },
  );

  els.forEach(function (el) {
    io.observe(el);
  });

  // Stagger siblings inside grids for a choreographed entrance
  [".bento", ".steps", ".work-grid"].forEach(function (sel) {
    document.querySelectorAll(sel).forEach(function (group) {
      Array.prototype.forEach.call(group.children, function (child, i) {
        child.style.transitionDelay = i * 70 + "ms";
      });
    });
  });
})();
