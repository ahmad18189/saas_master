(function () {
  "use strict";

  var SLIDE_MS = 5500;
  var POLL_MS = 3000;
  var I18N = {};
  var I18N_ALL = {};
  var slideIdx = 0;
  var slideTimer = null;
  var pollTimer = null;
  var lastStepIndex = -1;

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function loadI18n() {
    try {
      I18N = JSON.parse(($("sm-i18n") || {}).textContent || "{}") || {};
    } catch (e) {
      I18N = {};
    }
    try {
      I18N_ALL = JSON.parse(($("sm-i18n-all") || {}).textContent || "{}") || {};
    } catch (e) {
      I18N_ALL = {};
    }
  }

  function t(key) {
    return I18N[key] || key;
  }

  function applyDomI18n() {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (key && I18N[key] != null) el.textContent = I18N[key];
    });
    var title = t("st_title");
    if (title) document.title = title;
  }

  function applyStatusLang(code) {
    if (!code || !I18N_ALL[code]) return false;
    I18N = I18N_ALL[code];
    document.documentElement.setAttribute("lang", code);
    document.documentElement.setAttribute("dir", code === "ar" ? "rtl" : "ltr");
    document.documentElement.setAttribute("data-sm-lang", code);
    document.cookie = "sm_lang=" + code + "; path=/; max-age=31536000; SameSite=Lax";
    document.querySelectorAll(".sm-lang-btn").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-sm-lang") === code);
    });
    applyDomI18n();
    syncMobileSlide();
    // Refresh live step label from last known index
    if (lastStepIndex >= 0) {
      setStepUi(lastStepIndex, false);
    }
    return true;
  }

  window.smApplyStatusLang = applyStatusLang;
  // Reuse signup hook name so marketing.js live-switches without reload
  window.smApplySignupLang = applyStatusLang;

  function slides() {
    return Array.prototype.slice.call(document.querySelectorAll(".sm-status-slide"));
  }

  function slideKeys(i) {
    return { t: "st_slide" + (i + 1) + "_t", d: "st_slide" + (i + 1) + "_d" };
  }

  function syncMobileSlide() {
    var keys = slideKeys(slideIdx);
    var mt = document.querySelector("[data-i18n-slide-t]");
    var md = document.querySelector("[data-i18n-slide-d]");
    if (mt) mt.textContent = t(keys.t);
    if (md) md.textContent = t(keys.d);
  }

  function showSlide(idx) {
    var list = slides();
    if (!list.length) return;
    slideIdx = ((idx % list.length) + list.length) % list.length;
    list.forEach(function (el, i) {
      var on = i === slideIdx;
      el.classList.toggle("is-active", on);
      el.hidden = !on;
    });
    document.querySelectorAll("#status-dots [data-dot]").forEach(function (dot) {
      dot.classList.toggle("is-active", Number(dot.getAttribute("data-dot")) === slideIdx);
    });
    var bg = $("status-hero-bg");
    var active = list[slideIdx];
    if (bg && active) {
      var url = active.getAttribute("data-bg");
      if (url) {
        bg.classList.remove("is-swapping");
        // force reflow for animation restart
        void bg.offsetWidth;
        bg.style.backgroundImage = "url('" + url + "')";
        bg.classList.add("is-swapping");
      }
    }
    syncMobileSlide();
  }

  function startSlideshow() {
    showSlide(0);
    clearInterval(slideTimer);
    slideTimer = setInterval(function () {
      showSlide(slideIdx + 1);
    }, SLIDE_MS);
    var dots = $("status-dots");
    if (dots) {
      dots.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-dot]");
        if (!btn) return;
        clearInterval(slideTimer);
        showSlide(Number(btn.getAttribute("data-dot")));
        slideTimer = setInterval(function () {
          showSlide(slideIdx + 1);
        }, SLIDE_MS);
      });
    }
  }

  function labelForIndex(idx) {
    if (idx <= 0) return t("st_label_create");
    if (idx === 1) return t("st_label_template");
    if (idx >= 2 && idx <= 4) return t("st_label_account");
    if (idx >= 5) return t("st_label_https");
    return t("st_queue");
  }

  function setStepUi(stepIndex, doneAll) {
    lastStepIndex = stepIndex;
    var items = document.querySelectorAll("#status-checklist [data-step]");
    items.forEach(function (li) {
      var i = Number(li.getAttribute("data-step"));
      li.classList.remove("is-done", "is-current", "is-pending");
      if (doneAll || stepIndex > i) {
        li.classList.add("is-done");
      } else if (stepIndex === i) {
        li.classList.add("is-current");
      } else {
        li.classList.add("is-pending");
      }
    });
    var fill = $("status-bar-fill");
    if (fill) {
      var pct = doneAll ? 100 : Math.min(100, Math.round(((stepIndex + 0.35) / 6) * 100));
      fill.style.width = pct + "%";
    }
    var stepEl = $("status-step");
    if (stepEl && !doneAll) {
      stepEl.textContent = labelForIndex(stepIndex);
    }
  }

  function hideRunningHead() {
    var spin = $("spinner");
    if (spin) spin.style.display = "none";
  }

  function done(res) {
    clearInterval(pollTimer);
    hideRunningHead();
    var title = $("status-title");
    var stepEl = $("status-step");
    var detail = $("status-detail");
    var box = $("status-box");

    if (res.status === "Active") {
      setStepUi(6, true);
      if (title) title.textContent = t("st_ready");
      if (stepEl) stepEl.textContent = t("st_ready_sub");
      if (box) box.classList.add("is-ready");
      var email = "";
      var pw = "";
      try {
        email = sessionStorage.getItem("sm_owner_email") || "";
        pw = sessionStorage.getItem("sm_owner_password") || "";
        sessionStorage.removeItem("sm_owner_password");
      } catch (e) { /* ignore */ }
      var openUrl = res.site_url || ("https://" + (res.site_name || ""));
      if (openUrl && openUrl.indexOf("https://") !== 0 && res.site_name) {
        openUrl = "https://" + res.site_name;
      }
      var html = '<div class="sm-cred">';
      html +=
        "<div><strong>" +
        esc(t("st_store_address")) +
        ':</strong> <a href="' +
        esc(openUrl) +
        '" target="_blank" rel="noopener"><code>' +
        esc(openUrl) +
        "</code></a></div>";
      html +=
        "<div><strong>" +
        esc(t("st_domain")) +
        ":</strong> <code>" +
        esc(res.site_name) +
        "</code></div>";
      if (email) {
        html +=
          "<div><strong>" +
          esc(t("st_login")) +
          ":</strong> <code>" +
          esc(email) +
          "</code></div>";
      }
      if (pw) {
        html +=
          "<div><strong>" +
          esc(t("st_password")) +
          ":</strong> <code>" +
          esc(pw) +
          "</code> — " +
          esc(t("st_password_once")) +
          "</div>";
      }
      html += "</div>";
      if (openUrl) {
        html +=
          '<a class="sm-btn" href="' +
          esc(openUrl) +
          '" target="_blank" rel="noopener">' +
          esc(t("st_open_store")) +
          "</a>";
      }
      if (detail) detail.innerHTML = html;
    } else {
      if (title) title.textContent = t("st_failed");
      if (stepEl) stepEl.textContent = "";
      if (box) box.classList.add("is-failed");
      if (detail) {
        detail.innerHTML =
          '<p class="sm-status-error">' +
          esc(res.error || t("st_failed_sub")) +
          "</p>" +
          '<a class="sm-btn sm-btn-outline" href="/signup">' +
          esc(t("st_try_again")) +
          "</a>";
      }
    }
  }

  function poll() {
    var token = new URLSearchParams(window.location.search).get("token") || "";
    fetch("/api/method/saas_master.api.signup.get_status?token=" + encodeURIComponent(token), {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (r) {
        if (!r.ok) throw new Error("not found");
        return r.json();
      })
      .then(function (data) {
        var res = data.message || {};
        if (res.status === "Active" || res.status === "Failed") {
          done(res);
          return;
        }
        var idx = typeof res.step_index === "number" ? res.step_index : 0;
        setStepUi(idx, false);
        var title = $("status-title");
        if (title) title.textContent = t("st_creating");
      })
      .catch(function () {
        clearInterval(pollTimer);
        hideRunningHead();
        var title = $("status-title");
        var stepEl = $("status-step");
        var detail = $("status-detail");
        if (title) title.textContent = t("st_expired");
        if (stepEl) stepEl.textContent = "";
        if (detail) {
          detail.innerHTML =
            '<a class="sm-btn sm-btn-outline" href="/signup">' +
            esc(t("st_back_signup")) +
            "</a>";
        }
      });
  }

  loadI18n();
  applyDomI18n();
  startSlideshow();

  var token = new URLSearchParams(window.location.search).get("token") || "";
  if (!token) {
    window.location.href = "/signup";
  } else {
    poll();
    pollTimer = setInterval(poll, POLL_MS);
  }
})();
