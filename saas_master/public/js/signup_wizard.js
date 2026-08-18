/* Signup wizard — 5 steps incl. template picker, posts to saas_master.api.signup */
(function () {
  "use strict";

  var step = 1;
  var TOTAL = 5;
  var subdomainOk = false;
  var submitting = false;
  var templates = [];
  var selectedTemplate = null;
  var templatesLoaded = false;

  function $(id) { return document.getElementById(id); }
  function val(id) { return ($(id) && $(id).value || "").trim(); }

  var BASE_DOMAIN = ".flexloopers.com";
  var GEO = { countries: [], dial_codes: [], currencies: [], default_country: "Turkey" };
  var COUNTRY_BY_NAME = {};
  var phoneIti = null;

  function loadGeo() {
    var el = $("sm-geo");
    if (!el) return;
    try {
      GEO = JSON.parse(el.textContent || "{}") || GEO;
    } catch (e) {
      GEO = GEO;
    }
    (GEO.countries || []).forEach(function (c) {
      COUNTRY_BY_NAME[c.name] = c;
    });
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

  function dialCode() {
    if (phoneIti) {
      var data = phoneIti.getSelectedCountryData() || {};
      if (data.dialCode) return "+" + data.dialCode;
    }
    var c = selectedCountry();
    return (c && c.isd) || "+90";
  }

  function updatePhoneCode() {
    var iti = ensurePhoneInput();
    if (!iti) return;
    try {
      iti.setCountry(countryIso());
    } catch (e) { /* unknown ISO2 */ }
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
    return dialCode() + digits;
  }

  function showStep(n) {
    step = n;
    document.querySelectorAll(".sm-step").forEach(function (el) {
      el.hidden = el.dataset.step !== String(n);
    });
    document.querySelectorAll(".sm-progress span").forEach(function (el) {
      el.classList.toggle("done", Number(el.dataset.step) <= n);
    });
    $("btn-back").style.visibility = n > 1 ? "visible" : "hidden";
    $("btn-next").textContent = n === TOTAL ? "Create my store" : "Next";
    if (n === 2) ensureTemplates();
    if (n === 3) updatePhoneCode();
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
          var msg = "Something went wrong. Please try again.";
          try {
            var srv = JSON.parse(data._server_messages || "[]");
            if (srv.length) msg = JSON.parse(srv[0]).message || msg;
            else if (data.exception) msg = String(data.exception).split(":").pop();
          } catch (e) { /* keep default */ }
          throw new Error(msg);
        }
        return data.message;
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
    var t = templates.find(function (x) { return x.name === name; });
    if (t && t.industry) {
      var ind = $("industry");
      if (ind) ind.value = t.industry;
    }
  }

  function renderTemplates() {
    var grid = $("template-grid");
    if (!templates.length) {
      grid.innerHTML = '<div class="sm-error">No store templates are ready yet. Please try again later.</div>';
      return;
    }
    grid.setAttribute("role", "radiogroup");
    grid.setAttribute("aria-label", "Store look");
    grid.innerHTML = templates.map(function (t) {
      var primary = t.primary_color || "#121212";
      var accent = t.accent_color || "#111111";
      var media = t.preview_image
        ? '<div class="sm-template-media"><img class="sm-template-thumb" src="' +
          escapeHtml(t.preview_image) +
          '" alt="' +
          escapeHtml(t.title || t.name) +
          '" loading="lazy" decoding="async" width="800" height="420"></div>'
        : '<div class="sm-template-swatch" style="background:linear-gradient(135deg,' +
          escapeHtml(primary) +
          " 0%," +
          escapeHtml(accent) +
          ' 100%)"></div>';
      return (
        '<button type="button" class="sm-template-card" role="radio" aria-checked="false" tabindex="-1" data-name="' +
        escapeHtml(t.name) +
        '">' +
        media +
        '<div class="sm-template-meta">' +
        "<strong>" + escapeHtml(t.title || t.name) + "</strong>" +
        '<span class="sm-template-industry">' + escapeHtml(t.industry || "") + "</span>" +
        "<p>" + escapeHtml(t.description || "Starter store look and demo catalog.") + "</p>" +
        '<span class="sm-template-colors">' +
        '<i style="background:' + escapeHtml(primary) + '"></i>' +
        '<i style="background:' + escapeHtml(accent) + '"></i>' +
        "</span></div></button>"
      );
    }).join("");

    grid.querySelectorAll(".sm-template-card").forEach(function (card) {
      card.addEventListener("click", function () {
        selectTemplate(card.dataset.name);
        setErr(2, "");
      });
      card.addEventListener("keydown", function (event) {
        if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) return;
        event.preventDefault();
        var cards = Array.from(grid.querySelectorAll(".sm-template-card"));
        var direction = event.key === "ArrowLeft" || event.key === "ArrowUp" ? -1 : 1;
        var nextCard = cards[(cards.indexOf(card) + direction + cards.length) % cards.length];
        selectTemplate(nextCard.dataset.name);
        nextCard.focus();
      });
    });

    var preferred = null;
    var industry = val("industry");
    preferred = templates.find(function (t) { return t.industry === industry; })
      || templates.find(function (t) { return t.is_default; })
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
          '<div class="sm-error">' + escapeHtml(e.message || "Could not load templates.") + "</div>";
      });
  }

  function validStep1() {
    if (!val("company_name")) { setErr(1, "Please enter your company name."); return false; }
    setErr(1, ""); return true;
  }
  function validStep2() {
    if (!templates.length) {
      setErr(2, "No store templates are available yet.");
      return false;
    }
    if (!val("template")) {
      setErr(2, "Please choose a store look.");
      return false;
    }
    setErr(2, ""); return true;
  }
  function validStep3() {
    if (!val("owner_full_name")) { setErr(3, "Please enter your full name."); return false; }
    var email = val("owner_email");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setErr(3, "Please enter a valid email."); return false; }
    var phone = val("owner_phone");
    if (phone) {
      var iti = ensurePhoneInput();
      var ok = false;
      if (iti) {
        ok = (typeof iti.isValidNumber === "function" && iti.isValidNumber())
          || (typeof iti.isPossibleNumber === "function" && iti.isPossibleNumber());
      } else {
        var digits = phone.replace(/[^\d]/g, "");
        ok = digits.length >= 6 && digits.length <= 15 && !/[^\d\s\-()]/.test(phone);
      }
      if (!ok) {
        setErr(3, "Please enter a valid phone number for the selected country.");
        return false;
      }
    }
    if (val("owner_password").length < 8) { setErr(3, "Password must be at least 8 characters."); return false; }
    setErr(3, ""); return true;
  }
  function validStep4() {
    if (!subdomainOk) { setErr(4, "Please choose an available store address."); return false; }
    setErr(4, ""); return true;
  }

  var checkTimer = null;
  function checkSubdomain() {
    var box = $("subdomain-check");
    var sub = val("subdomain").toLowerCase();
    $("subdomain").value = sub;
    subdomainOk = false;
    if (!sub) { box.textContent = ""; return; }
    box.textContent = "Checking…";
    box.classList.remove("sm-ok");
    api("saas_master.api.signup.check_subdomain", { subdomain: sub })
      .then(function (res) {
        if (val("subdomain") !== sub) return;
        if (res.available) {
          subdomainOk = true;
          box.textContent = "✓ " + sub + BASE_DOMAIN + " is available";
          box.classList.add("sm-ok");
        } else {
          box.textContent = res.reason || "Not available.";
          box.classList.remove("sm-ok");
        }
      })
      .catch(function (e) { box.textContent = e.message; });
  }

  function selectedTitle() {
    var t = templates.find(function (x) { return x.name === val("template"); });
    return t ? (t.title || t.name) : val("template") || "—";
  }

  function renderReview() {
    var rows = [
      ["Company", val("company_name")],
      ["Store look", selectedTitle()],
      ["Industry", val("industry")],
      ["Country", val("country")],
      ["Currency", val("currency")],
      ["Owner", val("owner_full_name")],
      ["Email", val("owner_email")],
      ["Phone", fullPhone() || "—"],
      ["Current website", val("business_domain") || "—"],
      ["Store address", val("subdomain") + BASE_DOMAIN],
    ];
    $("review-list").innerHTML = rows
      .map(function (r) { return "<dt>" + r[0] + "</dt><dd>" + escapeHtml(r[1]) + "</dd>"; })
      .join("");
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function submit() {
    if (submitting) return;
    submitting = true;
    var btn = $("btn-next");
    btn.disabled = true;
    btn.textContent = "Creating…";
    api("saas_master.api.signup.create_tenant", {
      company_name: val("company_name"),
      industry: val("industry"),
      country: val("country"),
      currency: val("currency"),
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
        window.location.href = "/signup-status?token=" + encodeURIComponent(res.token);
      })
      .catch(function (e) {
        setErr(5, e.message);
        submitting = false;
        btn.disabled = false;
        btn.textContent = "Create my store";
      });
  }

  function next() {
    if (step === 1 && !validStep1()) return;
    if (step === 2 && !validStep2()) return;
    if (step === 3 && !validStep3()) return;
    if (step === 4 && !validStep4()) return;
    if (step === TOTAL) { submit(); return; }
    showStep(step + 1);
  }

  function init() {
    loadGeo();
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
    // Prefetch templates early
    ensureTemplates();
    showStep(1);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
