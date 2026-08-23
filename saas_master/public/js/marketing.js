(function () {
  var THEMES = [
    { id: "aqua", label: "Aqua" },
    { id: "teal", label: "Teal" },
    { id: "gold", label: "Gold" },
    { id: "coral", label: "Coral" },
    { id: "orange", label: "Orange" },
    { id: "rose", label: "Rose" },
    { id: "violet", label: "Violet" },
    { id: "indigo", label: "Indigo" },
    { id: "blue", label: "Blue" },
    { id: "cyan", label: "Cyan" },
    { id: "emerald", label: "Emerald" },
    { id: "lime", label: "Lime" },
    { id: "slate", label: "Slate" },
  ];
  var THEME_IDS = THEMES.map(function (t) { return t.id; });

  function readCookie(name) {
    var m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }

  function setLang(code) {
    if (!code) return;
    // Signup page: live translate AR / EN / TR without full reload
    if (typeof window.smApplySignupLang === "function" && window.smApplySignupLang(code)) {
      return;
    }
    document.cookie = "sm_lang=" + code + "; path=/; max-age=31536000; SameSite=Lax";
    var url = new URL(window.location.href);
    url.searchParams.set("lang", code);
    window.location.href = url.toString();
  }

  function closeThemeMenus(except) {
    document.querySelectorAll(".sm-theme-picker").forEach(function (picker) {
      if (except && picker === except) return;
      var menu = picker.querySelector(".sm-theme-menu");
      var trigger = picker.querySelector(".sm-theme-trigger");
      if (menu) menu.hidden = true;
      if (trigger) trigger.setAttribute("aria-expanded", "false");
    });
  }

  function syncThemeUi(code) {
    document.querySelectorAll(".sm-theme-btn[data-sm-theme]").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-sm-theme") === code);
    });
    document.querySelectorAll(".sm-theme-trigger").forEach(function (trigger) {
      var meta = THEMES.find(function (t) { return t.id === code; });
      trigger.title = (meta && meta.label) || "Accent color";
      trigger.setAttribute("aria-label", "Accent color: " + ((meta && meta.label) || code));
    });
  }

  function applyMode(mode, persist) {
    if (mode !== "dark" && mode !== "light") mode = "light";
    document.documentElement.setAttribute("data-sm-mode", mode);
    document.documentElement.style.colorScheme = mode;
    if (document.body) document.body.setAttribute("data-sm-mode", mode);
    document.querySelectorAll("[data-sm-mode-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", mode === "dark" ? "true" : "false");
      btn.title = mode === "dark" ? "Switch to light mode" : "Switch to dark mode";
      btn.setAttribute("aria-label", btn.title);
    });
    if (persist) {
      document.cookie = "sm_mode=" + mode + "; path=/; max-age=31536000; SameSite=Lax";
    }
  }

  function initMode() {
    var fromCookie = readCookie("sm_mode");
    var fromDom = document.documentElement.getAttribute("data-sm-mode");
    var fromSystem =
      window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    applyMode(fromCookie || fromDom || fromSystem, false);
  }

  function applyTheme(code, persist) {
    if (!code || THEME_IDS.indexOf(code) === -1) code = "teal";
    document.documentElement.setAttribute("data-sm-theme", code);
    if (document.body) document.body.setAttribute("data-sm-theme", code);
    syncThemeUi(code);
    if (persist) {
      document.cookie = "sm_theme=" + code + "; path=/; max-age=31536000; SameSite=Lax";
    }
  }

  function ensureThemeMenus() {
    document.querySelectorAll("[data-sm-theme-picker]").forEach(function (picker) {
      var menu = picker.querySelector(".sm-theme-menu");
      var grid = picker.querySelector(".sm-theme-grid");
      if (!menu || !grid || grid.childElementCount) return;
      THEMES.forEach(function (theme) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "sm-theme-btn";
        btn.setAttribute("data-sm-theme", theme.id);
        btn.title = theme.label;
        btn.setAttribute("aria-label", theme.label + " theme");
        btn.setAttribute("role", "option");
        grid.appendChild(btn);
      });
    });
  }

  function initTheme() {
    ensureThemeMenus();
    var fromUrl = new URL(window.location.href).searchParams.get("theme");
    var fromCookie = readCookie("sm_theme");
    var fromDom = document.documentElement.getAttribute("data-sm-theme");
    applyTheme(fromUrl || fromCookie || fromDom || "teal", false);
  }

  document.addEventListener("click", function (e) {
    var langBtn = e.target.closest("button[data-sm-lang], a[data-sm-lang]");
    if (langBtn) {
      e.preventDefault();
      setLang(langBtn.getAttribute("data-sm-lang"));
      return;
    }

    var trigger = e.target.closest(".sm-theme-trigger");
    if (trigger) {
      e.preventDefault();
      var picker = trigger.closest(".sm-theme-picker");
      var menu = picker && picker.querySelector(".sm-theme-menu");
      if (!menu) return;
      var open = menu.hidden;
      closeThemeMenus(picker);
      menu.hidden = !open;
      trigger.setAttribute("aria-expanded", open ? "true" : "false");
      return;
    }

    var themeBtn = e.target.closest("button.sm-theme-btn[data-sm-theme]");
    if (themeBtn) {
      e.preventDefault();
      applyTheme(themeBtn.getAttribute("data-sm-theme"), true);
      closeThemeMenus();
      return;
    }

    var modeBtn = e.target.closest("[data-sm-mode-toggle]");
    if (modeBtn) {
      e.preventDefault();
      var next = document.documentElement.getAttribute("data-sm-mode") === "dark" ? "light" : "dark";
      applyMode(next, true);
      return;
    }

    if (!e.target.closest(".sm-theme-picker")) closeThemeMenus();
  }, true);

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeThemeMenus();
  });

  var lang = document.documentElement.getAttribute("data-sm-lang");
  if (lang === "ar") {
    document.documentElement.setAttribute("dir", "rtl");
    document.body && document.body.classList.add("sm-rtl");
  }

  function initReveal() {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }
    var nodes = document.querySelectorAll(
      ".sm-section-head, .sm-pillar, .sm-audience-card, .sm-audience > div, .sm-demo-card, .sm-proof, .sm-banner, .sm-price-card, .sm-diff"
    );
    if (!nodes.length || !("IntersectionObserver" in window)) return;
    nodes.forEach(function (el) {
      el.classList.add("sm-reveal");
    });
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );
    nodes.forEach(function (el) {
      io.observe(el);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initTheme();
      initMode();
      initReveal();
    });
  } else {
    initTheme();
    initMode();
    initReveal();
  }
})();
