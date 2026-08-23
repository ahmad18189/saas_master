/* Signup wizard — 6 steps, i18n, plans, referral */
(function () {
  "use strict";

  var step = 1;
  var TOTAL = 6;
  var subdomainOk = false;
  var submitting = false;
  var templates = [];
  var selectedTemplate = null;
  var templatesLoaded = false;
  var I18N = {};
  var ALL_I18N = {};
  var ASIDE_STEPS = {};
  var currentLang = "en";
  var BASE_DOMAIN = ".flexloopers.com";
  var GEO = { countries: [], dial_codes: [], currencies: [], default_country: "Turkey" };
  var COUNTRY_BY_NAME = {};
  var phoneIti = null;

  function $(id) { return document.getElementById(id); }
  function val(id) { return ($(id) && $(id).value || "").trim(); }
  function t(key, fallback) {
    return I18N[key] || fallback || key;
  }

  function loadI18n() {
    var el = $("sm-i18n");
    if (el) {
      try { I18N = JSON.parse(el.textContent || "{}") || {}; } catch (e) { I18N = {}; }
    }
    var all = $("sm-i18n-all");
    if (all) {
      try { ALL_I18N = JSON.parse(all.textContent || "{}") || {}; } catch (e) { ALL_I18N = {}; }
    }
    currentLang = document.documentElement.getAttribute("data-sm-lang") || "en";
    if (ALL_I18N[currentLang]) I18N = ALL_I18N[currentLang];
  }

  function loadAsideSteps() {
    ASIDE_STEPS = {};
    var el = $("sm-aside-steps");
    if (!el) return;
    try {
      var list = JSON.parse(el.textContent || "[]") || [];
      list.forEach(function (s) {
        if (s && s.step) ASIDE_STEPS[String(s.step)] = s;
      });
    } catch (e) { ASIDE_STEPS = {}; }
  }

  function pickI18n(obj, lang) {
    if (!obj || typeof obj !== "object") return "";
    return obj[lang] || obj.en || "";
  }

  function updateAside(stepNum) {
    var data = ASIDE_STEPS[String(stepNum || step)] || ASIDE_STEPS["1"];
    if (!data) return;
    var lang = currentLang || "en";
    var bg = $("signup-aside-bg");
    var kicker = $("signup-aside-kicker");
    var title = $("signup-aside-title");
    var sub = $("signup-aside-sub");
    var bullets = $("signup-aside-bullets");
    if (bg && data.image) {
      bg.style.backgroundImage = "url('" + String(data.image).replace(/'/g, "%27") + "')";
      bg.classList.remove("is-swapping");
      // force reflow for fade
      void bg.offsetWidth;
      bg.classList.add("is-swapping");
    }
    if (kicker) kicker.textContent = pickI18n(data.kicker, lang);
    if (title) title.textContent = pickI18n(data.title, lang);
    if (sub) sub.textContent = pickI18n(data.subtitle, lang);
    if (bullets) {
      var html = (data.bullets || []).map(function (b) {
        var text = pickI18n(b.text, lang);
        if (!text) return "";
        return '<li><span class="sm-ico" aria-hidden="true">' + escapeHtml(b.icon || "") +
          "</span> <span>" + escapeHtml(text) + "</span></li>";
      }).join("");
      if (html) bullets.innerHTML = html;
    }
  }

  function applyDomI18n() {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (!key) return;
      var text = t(key);
      if (text && text !== key) el.textContent = text;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-placeholder");
      if (!key) return;
      var text = t(key);
      if (text && text !== key) el.setAttribute("placeholder", text);
    });
    var title = t("su_title");
    if (title && title !== "su_title") document.title = title;
    // refresh nav button label for current step
    if ($("btn-next")) {
      $("btn-next").textContent = step === TOTAL ? t("su_create", "Create my store") : t("su_next", "Next");
    }
    if ($("btn-back")) $("btn-back").textContent = t("su_back", "Back");
    updateAside(step);
    if (templatesLoaded) renderTemplates();
    refreshSubdomainStatusText();
  }

  function applySignupLang(code) {
    if (!code || !ALL_I18N[code]) return false;
    currentLang = code;
    I18N = ALL_I18N[code];
    document.documentElement.setAttribute("lang", code);
    document.documentElement.setAttribute("data-sm-lang", code);
    document.documentElement.setAttribute("dir", code === "ar" ? "rtl" : "ltr");
    if (document.body) {
      document.body.classList.toggle("sm-rtl", code === "ar");
      document.body.classList.add("sm-page", "sm-signup-page");
    }
    document.querySelectorAll(".sm-lang-btn[data-sm-lang]").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-sm-lang") === code);
    });
    document.cookie = "sm_lang=" + code + "; path=/; max-age=31536000; SameSite=Lax";
    try {
      var url = new URL(window.location.href);
      url.searchParams.set("lang", code);
      window.history.replaceState({}, "", url.toString());
    } catch (e) { /* ignore */ }
    applyDomI18n();
    if (step === TOTAL) renderReview();
    return true;
  }

  // Used by marketing.js language switcher (no full reload on signup)
  window.smApplySignupLang = applySignupLang;

  function loadGeo() {
    var el = $("sm-geo");
    if (!el) return;
    try { GEO = JSON.parse(el.textContent || "{}") || GEO; } catch (e) { /* keep */ }
    (GEO.countries || []).forEach(function (c) { COUNTRY_BY_NAME[c.name] = c; });
  }

  function selectedCountry() {
    var fromMap = COUNTRY_BY_NAME[val("country")] || COUNTRY_BY_NAME[GEO.default_country];
    if (fromMap) return fromMap;
    var sel = $("country");
    var opt = sel && sel.options[sel.selectedIndex];
    if (!opt) return null;
    return {
      name: opt.value,
      isd: opt.getAttribute("data-isd") || "+90",
      currency: opt.getAttribute("data-currency") || "",
      code: opt.getAttribute("data-code") || "",
    };
  }

  function countryIso() {
    var c = selectedCountry();
    return ((c && c.code) || "TR").toLowerCase();
  }

  function ensurePhoneInput() {
    if (phoneIti) return phoneIti;
    var input = $("owner_phone");
    var factory = window.intlTelInput;
    if (factory && typeof factory !== "function" && typeof factory.default === "function") {
      factory = factory.default;
    }
    if (!input || typeof factory !== "function") return null;
    phoneIti = factory(input, {
      initialCountry: countryIso(),
      countryOrder: ["tr", "sa", "ae", "eg", "us", "gb", "de"],
      separateDialCode: true,
      formatAsYouType: true,
      strictMode: true,
      countrySearch: true,
      autoPlaceholder: "aggressive",
    });
    return phoneIti;
  }

  function updatePhoneCode() {
    var iti = ensurePhoneInput();
    if (!iti) return;
    try { iti.setCountry(countryIso()); } catch (e) { /* ignore */ }
  }

  function updateCurrency() {
    var c = selectedCountry();
    if (c && c.currency && $("currency")) $("currency").value = c.currency;
  }

  function fullPhone() {
    if (phoneIti) {
      var e164 = phoneIti.getNumber() || "";
      if (e164) return e164;
    }
    var digits = val("owner_phone").replace(/[^\d]/g, "");
    if (!digits) return "";
    var c = selectedCountry();
    return ((c && c.isd) || "+90") + digits;
  }

  var stepDir = 1;

  function showStep(n) {
    var prev = step;
    stepDir = n >= prev ? 1 : -1;
    step = n;

    document.querySelectorAll(".sm-step").forEach(function (el) {
      var sn = Number(el.dataset.step);
      var on = sn === n;
      el.classList.remove("is-enter-fwd", "is-enter-back");
      el.hidden = !on;
      if (on) {
        void el.offsetWidth;
        el.classList.add(stepDir >= 0 ? "is-enter-fwd" : "is-enter-back");
        el.addEventListener(
          "animationend",
          function () {
            el.classList.remove("is-enter-fwd", "is-enter-back");
          },
          { once: true }
        );
      }
    });
    document.querySelectorAll(".sm-progress span").forEach(function (el) {
      el.classList.toggle("done", Number(el.dataset.step) <= n);
    });
    document.querySelectorAll("#progress-labels > span").forEach(function (el) {
      var s = Number(el.dataset.step);
      el.classList.toggle("active", s === n);
      el.classList.toggle("done", s < n);
    });
    $("btn-back").style.visibility = n > 1 ? "visible" : "hidden";
    $("btn-next").textContent = n === TOTAL ? t("su_create", "Create my store") : t("su_next", "Next");
    updateAside(n);
    if (n === 3) ensureTemplates();
    if (n === 4) updatePhoneCode();
    if (n === TOTAL) renderReview();
  }

  function setErr(n, msg) { $("err-" + n).textContent = msg || ""; }

  function api(method, params, isPost) {
    var url = "/api/method/" + method;
    var opts = { headers: { "X-Requested-With": "XMLHttpRequest" } };
    if (window.frappe && frappe.csrf_token) {
      opts.headers["X-Frappe-CSRF-Token"] = frappe.csrf_token;
    }
    if (isPost) {
      opts.method = "POST";
      opts.headers["Content-Type"] = "application/x-www-form-urlencoded";
      opts.body = new URLSearchParams(params).toString();
    } else {
      url += "?" + new URLSearchParams(params || {}).toString();
    }
    return fetch(url, opts).then(function (r) {
      return r.json().then(function (data) {
        if (!r.ok) {
          var msg = t("su_err_generic", "Something went wrong. Please try again.");
          try {
            var srv = JSON.parse(data._server_messages || "[]");
            if (srv.length) msg = JSON.parse(srv[0]).message || msg;
            else if (data.exception) msg = String(data.exception).split(":").pop();
          } catch (e) { /* keep */ }
          throw new Error(msg);
        }
        return data.message;
      });
    });
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function suggestPlan(band, support) {
    if (support === "dedicated" || band === "over_1000") return "Enterprise";
    if (band === "200_1000" || support === "chat") return "Growth";
    if (band === "50_200") return "Growth";
    return "Free";
  }

  function selectPlan(plan, fromSuggest) {
    $("signup_plan").value = plan;
    document.querySelectorAll(".sm-plan-card").forEach(function (card) {
      var on = card.dataset.plan === plan;
      card.classList.toggle("selected", on);
      var badge = card.querySelector(".sm-plan-badge");
      if (badge) badge.hidden = !(fromSuggest && on);
    });
  }

  function refreshPlanSuggestion() {
    var band = val("product_count_band");
    var support = val("support_need") || "chat";
    if (!band) return;
    var suggested = suggestPlan(band, support);
    selectPlan(suggested, true);
  }

  function wireChoices(rootId, attr, hiddenId, onChange) {
    var root = $(rootId);
    if (!root) return;
    root.querySelectorAll(".sm-choice").forEach(function (btn) {
      btn.addEventListener("click", function () {
        root.querySelectorAll(".sm-choice").forEach(function (b) { b.classList.remove("selected"); });
        btn.classList.add("selected");
        $(hiddenId).value = btn.getAttribute(attr) || "";
        if (onChange) onChange();
      });
    });
  }

  function selectTemplate(name) {
    selectedTemplate = name;
    $("template").value = name || "";
    document.querySelectorAll(".sm-template-card").forEach(function (card) {
      var isSelected = card.dataset.name === name;
      card.classList.toggle("selected", isSelected);
      card.setAttribute("aria-checked", String(isSelected));
      card.tabIndex = isSelected ? 0 : -1;
    });
    var tmpl = templates.find(function (x) { return x.name === name; });
    if (tmpl && tmpl.industry) {
      var ind = $("industry");
      if (ind) ind.value = tmpl.industry;
    }
  }

  function templateTitle(tmpl) {
    return pickI18n(tmpl.title_i18n, currentLang) || tmpl.title || tmpl.name || "";
  }

  function templateDescription(tmpl) {
    return pickI18n(tmpl.description_i18n, currentLang) || tmpl.description || "";
  }

  function templateImage(tmpl) {
    return pickI18n(tmpl.preview_image_i18n, currentLang) || tmpl.preview_image || "";
  }

  function renderTemplates() {
    var grid = $("template-grid");
    if (!templates.length) {
      grid.innerHTML = '<div class="sm-error">' + escapeHtml(t("su_err_no_templates")) + "</div>";
      return;
    }
    var selected = val("template");
    grid.setAttribute("role", "radiogroup");
    grid.innerHTML = templates.map(function (tmpl) {
      var primary = tmpl.primary_color || "#121212";
      var accent = tmpl.accent_color || "#111111";
      var title = templateTitle(tmpl);
      var image = templateImage(tmpl);
      var media = image
        ? '<div class="sm-template-media"><img class="sm-template-thumb" src="' +
          escapeHtml(image) +
          '" alt="' + escapeHtml(title) +
          '" loading="lazy" decoding="async" width="800" height="420"></div>'
        : '<div class="sm-template-swatch" style="background:linear-gradient(135deg,' +
          escapeHtml(primary) + " 0%," + escapeHtml(accent) + ' 100%)"></div>';
      return (
        '<button type="button" class="sm-template-card" role="radio" aria-checked="false" tabindex="-1" data-name="' +
        escapeHtml(tmpl.name) + '">' + media +
        '<div class="sm-template-meta"><strong>' + escapeHtml(title) + "</strong>" +
        '<span class="sm-template-industry">' + escapeHtml(industryLabel(tmpl.industry || "")) + "</span>" +
        "<p>" + escapeHtml(templateDescription(tmpl)) + "</p>" +
        '<span class="sm-template-colors"><i style="background:' + escapeHtml(primary) +
        '"></i><i style="background:' + escapeHtml(accent) + '"></i></span></div></button>'
      );
    }).join("");

    grid.querySelectorAll(".sm-template-card").forEach(function (card) {
      card.addEventListener("click", function () {
        selectTemplate(card.dataset.name);
        setErr(3, "");
      });
    });

    if (selected && templates.some(function (x) { return x.name === selected; })) {
      selectTemplate(selected);
      return;
    }
    var industry = val("industry");
    var preferred = templates.find(function (x) { return x.industry === industry; })
      || templates.find(function (x) { return x.is_default; })
      || templates[0];
    if (preferred) selectTemplate(preferred.name);
  }

  function ensureTemplates() {
    if (templatesLoaded) return;
    api("saas_master.api.signup.list_templates", {})
      .then(function (rows) {
        templates = rows || [];
        templatesLoaded = true;
        renderTemplates();
      })
      .catch(function (e) {
        $("template-grid").innerHTML =
          '<div class="sm-error">' + escapeHtml(e.message || t("su_err_no_templates")) + "</div>";
      });
  }

  function validStep1() {
    if (!val("company_name")) { setErr(1, t("su_err_company")); return false; }
    setErr(1, ""); return true;
  }
  function validStep2() {
    if (!val("product_count_band")) { setErr(2, t("su_err_products")); return false; }
    if (!val("signup_plan")) { setErr(2, t("su_err_plan")); return false; }
    setErr(2, ""); return true;
  }
  function validStep3() {
    if (!templates.length) { setErr(3, t("su_err_no_templates")); return false; }
    if (!val("template")) { setErr(3, t("su_err_template")); return false; }
    setErr(3, ""); return true;
  }
  function validStep4() {
    if (!val("owner_full_name")) { setErr(4, t("su_err_name")); return false; }
    var email = val("owner_email");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setErr(4, t("su_err_email")); return false; }
    var phone = val("owner_phone");
    if (phone) {
      var iti = ensurePhoneInput();
      var ok = false;
      if (iti) {
        ok = (typeof iti.isValidNumber === "function" && iti.isValidNumber())
          || (typeof iti.isPossibleNumber === "function" && iti.isPossibleNumber());
      } else {
        var digits = phone.replace(/[^\d]/g, "");
        ok = digits.length >= 6 && digits.length <= 15;
      }
      if (!ok) { setErr(4, t("su_err_phone")); return false; }
    }
    if (val("owner_password").length < 8) { setErr(4, t("su_err_password")); return false; }
    if (!val("referral_source")) { setErr(4, t("su_err_heard")); return false; }
    setErr(4, ""); return true;
  }
  function validStep5() {
    if (!subdomainOk) { setErr(5, t("su_err_subdomain")); return false; }
    setErr(5, ""); return true;
  }

  var checkTimer = null;
  var lastSubdomainCode = "";
  function subdomainReasonMessage(code) {
    return ({
      invalid: t("su_err_sub_invalid"),
      reserved: t("su_err_sub_reserved"),
      taken: t("su_err_sub_taken"),
    })[code] || t("su_err_sub_unavailable", "Not available.");
  }

  function refreshSubdomainStatusText() {
    var box = $("subdomain-check");
    if (!box) return;
    var sub = val("subdomain").toLowerCase();
    if (!sub) { box.textContent = ""; return; }
    if (subdomainOk) {
      box.textContent = "✓ " + sub + BASE_DOMAIN + " " + t("su_available", "is available");
      box.classList.add("sm-ok");
      return;
    }
    if (lastSubdomainCode) {
      box.textContent = subdomainReasonMessage(lastSubdomainCode);
      box.classList.remove("sm-ok");
    }
  }

  function checkSubdomain() {
    var box = $("subdomain-check");
    var sub = val("subdomain").toLowerCase();
    $("subdomain").value = sub;
    subdomainOk = false;
    lastSubdomainCode = "";
    if (!sub) { box.textContent = ""; return; }
    box.textContent = t("su_checking", "Checking…");
    box.classList.remove("sm-ok");
    api("saas_master.api.signup.check_subdomain", { subdomain: sub })
      .then(function (res) {
        if (val("subdomain") !== sub) return;
        if (res.available) {
          subdomainOk = true;
          lastSubdomainCode = "";
          box.textContent = "✓ " + sub + BASE_DOMAIN + " " + t("su_available", "is available");
          box.classList.add("sm-ok");
        } else {
          lastSubdomainCode = res.reason_code || "";
          box.textContent = subdomainReasonMessage(lastSubdomainCode);
          box.classList.remove("sm-ok");
        }
      })
      .catch(function (e) { box.textContent = e.message; });
  }

  function selectedTitle() {
    var tmpl = templates.find(function (x) { return x.name === val("template"); });
    return tmpl ? (templateTitle(tmpl) || tmpl.name) : val("template") || "—";
  }

  function bandLabel(band) {
    return ({
      under_50: t("su_band_50"),
      "50_200": t("su_band_200"),
      "200_1000": t("su_band_1000"),
      over_1000: t("su_band_plus"),
    })[band] || band;
  }

  function heardLabel(code) {
    return ({
      google: t("su_heard_google"),
      social: t("su_heard_social"),
      friend: t("su_heard_friend"),
      compare_platforms: t("su_heard_compare"),
      compare_salla_zid: t("su_heard_compare"),
      youtube: t("su_heard_youtube"),
      event: t("su_heard_event"),
      other: t("su_heard_other"),
    })[code] || code;
  }

  function planLabel(plan) {
    return ({
      Free: t("su_plan_free"),
      Growth: t("su_plan_growth"),
      Enterprise: t("su_plan_ent"),
    })[plan] || plan;
  }

  function industryLabel(code) {
    return ({
      Clothing: t("su_ind_clothing"),
      Electronics: t("su_ind_electronics"),
      Beauty: t("su_ind_beauty"),
      Home: t("su_ind_home"),
      Grocery: t("su_ind_grocery"),
      Services: t("su_ind_services"),
      Other: t("su_ind_other"),
    })[code] || code;
  }

  function renderReview() {
    var rows = [
      [t("su_rev_company"), val("company_name")],
      [t("su_rev_city"), val("company_city") || "—"],
      [t("su_rev_plan"), planLabel(val("signup_plan"))],
      [t("su_rev_products"), bandLabel(val("product_count_band"))],
      [t("su_rev_look"), selectedTitle()],
      [t("su_rev_industry"), industryLabel(val("industry"))],
      [t("su_rev_country"), val("country")],
      [t("su_rev_currency"), val("currency")],
      [t("su_rev_owner"), val("owner_full_name")],
      [t("su_rev_email"), val("owner_email")],
      [t("su_rev_phone"), fullPhone() || "—"],
      [t("su_rev_heard"), heardLabel(val("referral_source"))],
      [t("su_rev_website"), val("business_domain") || "—"],
      [t("su_rev_address"), val("subdomain") + BASE_DOMAIN],
    ];
    $("review-list").innerHTML = rows
      .map(function (r) { return "<dt>" + escapeHtml(r[0]) + "</dt><dd>" + escapeHtml(r[1]) + "</dd>"; })
      .join("");
  }

  function submit() {
    if (submitting) return;
    submitting = true;
    var btn = $("btn-next");
    btn.disabled = true;
    btn.textContent = t("su_creating", "Creating…");
    api("saas_master.api.signup.create_tenant", {
      company_name: val("company_name"),
      company_city: val("company_city"),
      company_description: val("company_description"),
      industry: val("industry"),
      country: val("country"),
      currency: val("currency"),
      product_count_band: val("product_count_band"),
      support_need: val("support_need"),
      signup_plan: val("signup_plan"),
      referral_source: val("referral_source"),
      owner_full_name: val("owner_full_name"),
      owner_email: val("owner_email"),
      owner_phone: fullPhone(),
      business_domain: val("business_domain"),
      subdomain: val("subdomain"),
      owner_password: val("owner_password"),
      template: val("template"),
      website: val("hp_website"),
    }, true)
      .then(function (res) {
        try {
          sessionStorage.setItem("sm_owner_email", val("owner_email"));
          sessionStorage.setItem("sm_owner_password", val("owner_password"));
        } catch (e) { /* private mode */ }
        var lang = document.documentElement.getAttribute("data-sm-lang") || "en";
        window.location.href = "/signup-status?token=" + encodeURIComponent(res.token) + "&lang=" + encodeURIComponent(lang);
      })
      .catch(function (e) {
        setErr(6, e.message);
        submitting = false;
        btn.disabled = false;
        btn.textContent = t("su_create", "Create my store");
      });
  }

  function next() {
    if (step === 1 && !validStep1()) return;
    if (step === 2 && !validStep2()) return;
    if (step === 3 && !validStep3()) return;
    if (step === 4 && !validStep4()) return;
    if (step === 5 && !validStep5()) return;
    if (step === TOTAL) { submit(); return; }
    showStep(step + 1);
  }

  function init() {
    loadI18n();
    loadAsideSteps();
    loadGeo();
    // Language switcher (AR / EN / TR) — also handled by marketing.js
    document.querySelectorAll(".sm-lang-btn[data-sm-lang]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        applySignupLang(btn.getAttribute("data-sm-lang"));
      });
    });
    wireChoices("product-bands", "data-band", "product_count_band", refreshPlanSuggestion);
    wireChoices("support-need", "data-support", "support_need", refreshPlanSuggestion);
    wireChoices("referral-source", "data-ref", "referral_source");
    document.querySelectorAll(".sm-plan-card").forEach(function (card) {
      card.addEventListener("click", function () {
        selectPlan(card.dataset.plan, false);
        setErr(2, "");
      });
    });
    $("btn-next").addEventListener("click", next);
    $("btn-back").addEventListener("click", function () { if (step > 1) showStep(step - 1); });
    $("country").addEventListener("change", function () {
      updateCurrency();
      updatePhoneCode();
    });
    $("subdomain").addEventListener("input", function () {
      clearTimeout(checkTimer);
      checkTimer = setTimeout(checkSubdomain, 400);
    });
    ensureTemplates();
    showStep(1);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
