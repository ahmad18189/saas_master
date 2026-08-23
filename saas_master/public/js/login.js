/* Master login — merchant store finder + Frappe operator auth overrides */
(function () {
  "use strict";

  var I18N = {};
  var ALL_I18N = {};
  var currentLang = "en";
  var BASE_DOMAIN = ".flexloopers.com";
  var resolving = false;

  function $(id) {
    return document.getElementById(id);
  }

  function t(key, fallback) {
    return I18N[key] || fallback || key;
  }

  function loadI18n() {
    var el = $("sm-i18n");
    if (el) {
      try {
        I18N = JSON.parse(el.textContent || "{}") || {};
      } catch (e) {
        I18N = {};
      }
    }
    var all = $("sm-i18n-all");
    if (all) {
      try {
        ALL_I18N = JSON.parse(all.textContent || "{}") || {};
      } catch (e) {
        ALL_I18N = {};
      }
    }
    currentLang = document.documentElement.getAttribute("data-sm-lang") || "en";
    if (ALL_I18N[currentLang]) I18N = ALL_I18N[currentLang];
  }

  function applyLoginLang(code) {
    if (!code || !ALL_I18N[code]) return false;
    currentLang = code;
    I18N = ALL_I18N[code];
    document.cookie = "sm_lang=" + code + "; path=/; max-age=31536000; SameSite=Lax";
    document.documentElement.setAttribute("data-sm-lang", code);
    document.documentElement.setAttribute("lang", code);
    document.documentElement.setAttribute("dir", code === "ar" ? "rtl" : "ltr");
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (key && I18N[key]) el.textContent = I18N[key];
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-placeholder");
      if (key && I18N[key]) el.setAttribute("placeholder", I18N[key]);
    });
    document.querySelectorAll(".sm-lang-btn").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-sm-lang") === code);
    });
    var url = new URL(window.location.href);
    url.searchParams.set("lang", code);
    window.history.replaceState({}, "", url.toString());
    return true;
  }

  window.smApplySignupLang = applyLoginLang;

  function setErr(msg) {
    var box = $("store-login-err");
    if (!box) return;
    if (!msg) {
      box.hidden = true;
      box.textContent = "";
      return;
    }
    box.hidden = false;
    box.textContent = msg;
  }

  function clearChoices() {
    var box = $("store-login-choices");
    if (!box) return;
    box.hidden = true;
    box.innerHTML = "";
  }

  function showChoices(choices) {
    var box = $("store-login-choices");
    if (!box) return;
    box.innerHTML = "";
    if (!choices || !choices.length) {
      box.hidden = true;
      return;
    }
    var title = document.createElement("p");
    title.className = "sm-hint";
    title.textContent = t("lg_pick_store", "Choose a store:");
    box.appendChild(title);
    choices.forEach(function (c) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sm-choice sm-login-choice";
      var label = (c.subdomain || "") + BASE_DOMAIN;
      if (c.status && c.status !== "Active") {
        label += " (" + c.status + ")";
      }
      btn.textContent = label;
      btn.addEventListener("click", function () {
        if (c.url) {
          window.location.href = c.url;
          return;
        }
        if (c.subdomain) {
          var input = $("store_subdomain");
          if (input) input.value = c.subdomain;
          clearChoices();
          resolveAndGo({ subdomain: c.subdomain });
        }
      });
      box.appendChild(btn);
    });
    box.hidden = false;
  }

  function api(method, args) {
    return new Promise(function (resolve, reject) {
      frappe.call({
        method: method,
        args: args || {},
        type: "POST",
        freeze: false,
        callback: function (r) {
          if (r && r.exc) {
            reject(r);
            return;
          }
          resolve(r && r.message);
        },
        error: function (r) {
          reject(r);
        },
      });
    });
  }

  function reasonMessage(reason, status) {
    if (reason === "provisioning") {
      return t("lg_err_provisioning", "Your store is still being built. Try again in a few minutes.");
    }
    if (reason === "unavailable") {
      return t("lg_err_unavailable", "This store is not available right now.");
    }
    if (reason === "multiple") {
      return t("lg_err_multiple", "We found more than one store for that email. Pick one below.");
    }
    return t("lg_err_not_found", "We couldn't find that store. Check the address or create a new one.");
  }

  function resolveAndGo(args) {
    if (resolving) return;
    resolving = true;
    setErr("");
    clearChoices();
    var btn = $("btn-open-store");
    if (btn) {
      btn.disabled = true;
      btn.textContent = t("lg_checking", "Checking…");
    }
    api("saas_master.api.login.resolve_store", args)
      .then(function (res) {
        res = res || {};
        if (res.ok && res.url) {
          window.location.href = res.url;
          return;
        }
        if (res.reason === "multiple" && res.choices && res.choices.length) {
          setErr(reasonMessage("multiple"));
          showChoices(res.choices);
          return;
        }
        setErr(reasonMessage(res.reason, res.status));
      })
      .catch(function () {
        setErr(t("lg_err_generic", "Something went wrong. Please try again."));
      })
      .finally(function () {
        resolving = false;
        if (btn) {
          btn.disabled = false;
          btn.textContent = t("lg_continue", "Continue to store");
        }
      });
  }

  function onStoreSubmit(ev) {
    if (ev) ev.preventDefault();
    var sub = (($("store_subdomain") && $("store_subdomain").value) || "").trim().toLowerCase();
    var email = (($("store_email") && $("store_email").value) || "").trim().toLowerCase();
    if ($("store_subdomain")) $("store_subdomain").value = sub;
    if (!sub && !email) {
      setErr(t("lg_err_empty", "Enter your store address or the email you signed up with."));
      return false;
    }
    if (sub) {
      resolveAndGo({ subdomain: sub });
    } else {
      resolveAndGo({ email: email });
    }
    return false;
  }

  function hideAllPanels() {
    document.querySelectorAll(".sm-login-panel, section.for-store-login, section.for-login, section.for-forgot, section.for-login-with-email-link, section.for-email-login, section.for-signup").forEach(function (el) {
      el.classList.remove("sm-panel-active");
      el.style.display = "none";
    });
  }

  function showPanel(selector) {
    hideAllPanels();
    var el = document.querySelector(selector);
    if (el) {
      el.classList.add("sm-panel-active");
      el.style.display = "";
    }
  }

  function patchFrappeLogin() {
    if (typeof window.login === "undefined") return;

    var origReset = login.reset_sections;
    login.reset_sections = function (hide) {
      if (typeof origReset === "function") origReset(hide);
      hideAllPanels();
    };

    login.login = function () {
      showPanel(".for-store-login");
    };

    login.platform = function () {
      showPanel(".for-login");
      var email = $("login_email");
      if (email) email.focus();
    };

    login.forgot = function () {
      if ($("login_email") && $("login_email").value && $("forgot_email")) {
        $("forgot_email").value = $("login_email").value;
      }
      showPanel(".for-forgot");
      var inp = $("forgot_email");
      if (inp) inp.focus();
    };

    login.login_with_email_link = function () {
      if ($("login_email") && $("login_email").value && $("login_with_email_link_email")) {
        $("login_with_email_link_email").value = $("login_email").value;
      }
      showPanel(".for-login-with-email-link");
      var inp = $("login_with_email_link_email");
      if (inp) inp.focus();
    };

    login.signup = function () {
      var lang = document.documentElement.getAttribute("data-sm-lang") || "en";
      window.location.href = "/signup?lang=" + encodeURIComponent(lang);
    };

    // Back links inside forgot / email-link use #platform
    login.route = function () {
      var route = (window.location.hash || "#login").slice(1) || "login";
      route = route.replaceAll("-", "_");
      if (typeof login[route] === "function") {
        login[route]();
      } else {
        login.login();
      }
    };
  }

  function maybeForcePlatform() {
    try {
      var params = new URLSearchParams(window.location.search);
      if (params.get("redirect-to") && (!window.location.hash || window.location.hash === "#login")) {
        window.location.hash = "#platform";
        return true;
      }
    } catch (e) { /* ignore */ }
    return false;
  }

  function init() {
    loadI18n();
    patchFrappeLogin();

    var form = $("form-store-login");
    if (form) {
      form.addEventListener("submit", onStoreSubmit);
    }

    maybeForcePlatform();
    if (typeof login !== "undefined" && typeof login.route === "function") {
      login.route();
    } else {
      showPanel(".for-store-login");
    }
  }

  if (window.frappe && frappe.ready) {
    frappe.ready(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
