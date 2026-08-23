(function () {
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function uid(type) {
    return type + "_" + Math.random().toString(36).slice(2, 9);
  }

  var I18N_LANGS = ["ar", "en", "tr"];

  function hydrateI18n(props, prefix) {
    var map = props[prefix + "_i18n"];
    if (map && typeof map === "object" && !Array.isArray(map)) return Object.assign({}, map);
    var out = {};
    I18N_LANGS.forEach(function (code) {
      var v = props[prefix + "_" + code];
      if (v != null && String(v) !== "") out[code] = v;
    });
    if (!Object.keys(out).length && props[prefix]) out.en = props[prefix];
    return out;
  }

  function resolveI18n(map, lang, fallback) {
    if (!map || typeof map !== "object") return fallback || "";
    return map[lang] || map.en || map.ar || (Object.keys(map)[0] ? map[Object.keys(map)[0]] : "") || fallback || "";
  }

  function i18nRowsFromMap(map) {
    var rows = [];
    I18N_LANGS.forEach(function (code) {
      if (map[code] != null && String(map[code]) !== "") rows.push({ lang: code, value: map[code] });
    });
    if (!rows.length) rows.push({ lang: "en", value: "" });
    return rows;
  }

  function mapFromI18nRows(rows) {
    var out = {};
    (rows || []).forEach(function (r) {
      if (r && r.lang) out[r.lang] = r.value == null ? "" : r.value;
    });
    return out;
  }

  function labelOf(item, lang) {
    if (!item) return "";
    if (typeof item.label === "string") return item.label;
    return (item.label && (item.label[lang] || item.label.en || item.label.ar)) || item.type;
  }

  function setDeep(obj, path, value) {
    var parts = path.split(".");
    var cur = obj;
    for (var i = 0; i < parts.length - 1; i++) {
      var k = parts[i];
      var idx = /^\d+$/.test(k) ? Number(k) : k;
      if (cur[idx] == null) cur[idx] = /^\d+$/.test(parts[i + 1]) ? [] : {};
      cur = cur[idx];
    }
    var last = parts[parts.length - 1];
    cur[/^\d+$/.test(last) ? Number(last) : last] = value;
  }

  function brandHtml(mark) {
    mark = mark || "Dukan";
    if (mark.length > 2) return esc(mark.slice(0, 2)) + "<span>" + esc(mark.slice(2)) + "</span>";
    return esc(mark);
  }

  window.MarketingEditor = {
    async mount(host, opts) {
      var call = opts.call;
      var toast = opts.toast || alert;
      var lang = opts.lang || "en";
      if (I18N_LANGS.indexOf(lang) < 0) lang = "en";

      host.innerHTML = '<p class="sl-loading" style="padding:2rem">Loading editor…</p>';
      var state = await call("saas_master.api.marketing_editor.get_page", {});
      var blocks = Array.isArray(state.draft_blocks) ? state.draft_blocks.slice() : [];
      var selected = blocks[0] ? blocks[0].id : null;
      var selectedMedia = null;
      var foldState = {};
      var viewport = "lg";
      var dirty = false;
      var catalog = state.catalog || [];
      var chrome = state.chrome || {};
      if (!chrome.footer_legal_i18n) {
        chrome.footer_legal_i18n = Object.assign({}, chrome.footer_copy_i18n || hydrateI18n(chrome, "footer_copy"));
      }
      if (!chrome.copyright_year) chrome.copyright_year = String(new Date().getFullYear());
      var showChrome = true;
      var focusCanvas = false;

      var groups = {
        layout: "Layout",
        content: "Content",
        interaction: "Interaction",
        advanced: "Advanced",
        other: "Other",
      };

      function chromeText(key, fallback) {
        return resolveI18n(hydrateI18n(chrome, key), lang, fallback || key);
      }

      function editingChrome() {
        return selected === "__header__" || selected === "__footer__";
      }

      function chromeUrl(key, fallback) {
        var v = chrome[key];
        return v == null || v === "" ? fallback : v;
      }

      function captureScroll() {
        var wrap = host.querySelector(".sl-ed-canvas-wrap");
        var props = host.querySelector(".sl-ed-props");
        var left = host.querySelector(".sl-ed-blocks");
        return {
          canvas: wrap ? wrap.scrollTop : 0,
          props: props ? props.scrollTop : 0,
          left: left ? left.scrollTop : 0,
        };
      }

      function restoreScroll(pos) {
        if (!pos) return;
        var apply = function () {
          var wrap = host.querySelector(".sl-ed-canvas-wrap");
          var props = host.querySelector(".sl-ed-props");
          var left = host.querySelector(".sl-ed-blocks");
          if (wrap) wrap.scrollTop = pos.canvas;
          if (props) props.scrollTop = pos.props;
          if (left) left.scrollTop = pos.left;
        };
        apply();
        requestAnimationFrame(apply);
      }

      var allowLeave = false;
      window.addEventListener("beforeunload", function (e) {
        if (!dirty || allowLeave) return;
        e.preventDefault();
        e.returnValue = "";
      });

      function markDirty() {
        dirty = true;
        var el = host.querySelector(".sl-ed-meta");
        if (el) {
          el.textContent = "Unsaved changes";
          el.classList.remove("is-saved");
        }
        var badge = host.querySelector(".sl-badge");
        if (badge) {
          badge.textContent = "Draft";
          badge.className = "sl-badge stub";
        }
      }

      function catalogItem(type) {
        return catalog.find(function (c) {
          return c.type === type;
        });
      }

      function addBlock(type) {
        var c = catalogItem(type);
        if (!c) return;
        var block = { id: uid(type), type: type, props: JSON.parse(JSON.stringify(c.defaults || {})) };
        blocks.push(block);
        selected = block.id;
        markDirty();
        paint();
      }

      function removeBlock(id) {
        blocks = blocks.filter(function (b) {
          return b.id !== id;
        });
        if (selected === id) selected = blocks[0] ? blocks[0].id : null;
        markDirty();
        paint();
      }

      function moveBlock(id, dir) {
        var i = blocks.findIndex(function (b) {
          return b.id === id;
        });
        var j = i + dir;
        if (i < 0 || j < 0 || j >= blocks.length) return;
        var tmp = blocks[i];
        blocks[i] = blocks[j];
        blocks[j] = tmp;
        markDirty();
        paint();
      }

      function selectedBlock() {
        return (
          blocks.find(function (b) {
            return b.id === selected;
          }) || null
        );
      }

      function demoImages() {
        var imgs = [];
        blocks.forEach(function (b) {
          if (b.type !== "demos") return;
          ((b.props && b.props.items) || []).forEach(function (d) {
            if (d && d.image) imgs.push(d.image);
          });
        });
        return imgs;
      }

      function wrapSection(block, inner) {
        var c = catalogItem(block.type);
        var label = labelOf(c, lang) || block.type;
        return (
          '<div class="sl-ed-section' +
          (selected === block.id ? " is-selected" : "") +
          '" data-id="' +
          esc(block.id) +
          '"><span class="sl-ed-section-badge">' +
          esc(label) +
          "</span>" +
          inner +
          "</div>"
        );
      }

      function ed(spec) {
        return ' contenteditable="true" spellcheck="false" data-bind="' + esc(spec) + '"';
      }

      function renderChromeTop() {
        if (!showChrome) return "";
        return (
          '<div class="sl-ed-section sl-ed-chrome-hit' +
          (selected === "__header__" ? " is-selected" : "") +
          '" data-chrome-sel="header"><span class="sl-ed-section-badge">Header</span>' +
          '<div class="sm-topbar"><div class="sm-wrap sm-topbar-inner">' +
          '<span class="sm-topbar-msg"' +
          ed("chrome:announcement") +
          ">" +
          esc(chromeText("announcement", "")) +
          "</span>" +
          '<div class="sm-topbar-tools"><div class="sm-lang">' +
          I18N_LANGS.map(function (code) {
            return (
              '<span class="sm-lang-btn' +
              (code === lang ? " active" : "") +
              '">' +
              code.toUpperCase() +
              "</span>"
            );
          }).join("") +
          "</div></div></div></div>" +
          '<header class="sm-header"><div class="sm-wrap sm-header-inner">' +
          '<a class="sm-logo" href="/"' +
          ed("chrome:brand_mark") +
          ">" +
          brandHtml(chrome.brand_mark || "Dukan") +
          "</a>" +
          '<nav class="sm-nav">' +
          '<a href="' +
          esc(chromeUrl("nav_solutions_url", "/solutions")) +
          '"' +
          ed("chrome:nav_solutions") +
          ">" +
          esc(chromeText("nav_solutions", "Solutions")) +
          "</a>" +
          '<a href="' +
          esc(chromeUrl("nav_pricing_url", "/pricing")) +
          '"' +
          ed("chrome:nav_pricing") +
          ">" +
          esc(chromeText("nav_pricing", "Pricing")) +
          "</a>" +
          '<a href="' +
          esc(chromeUrl("nav_templates_url", "#templates")) +
          '"' +
          ed("chrome:nav_templates") +
          ">" +
          esc(chromeText("nav_templates", "Templates")) +
          "</a>" +
          '<a href="' +
          esc(chromeUrl("nav_login_url", "/login")) +
          '"' +
          ed("chrome:nav_login") +
          ">" +
          esc(chromeText("nav_login", "Login")) +
          "</a></nav>" +
          '<a class="sm-btn sm-btn-sm" href="' +
          esc(chromeUrl("cta_create_url", "/signup")) +
          '"' +
          ed("chrome:cta_create") +
          ">" +
          esc(chromeText("cta_create", "Create your store")) +
          "</a></div></header></div>"
        );
      }

      function renderChromeFooter() {
        if (!showChrome) return "";
        return (
          '<div class="sl-ed-section sl-ed-chrome-hit' +
          (selected === "__footer__" ? " is-selected" : "") +
          '" data-chrome-sel="footer"><span class="sl-ed-section-badge">Footer</span>' +
          '<footer class="sm-footer"><div class="sm-wrap sm-footer-inner">' +
          '<div class="sm-footer-brand"><a class="sm-logo" href="/"' +
          ed("chrome:brand_mark") +
          ">" +
          brandHtml(chrome.brand_mark || "Dukan") +
          "</a><p" +
          ed("chrome:footer_copy") +
          ">" +
          esc(chromeText("footer_copy", "")) +
          "</p></div>" +
          '<div class="sm-footer-cols"><div><strong>' +
          esc(chromeText("nav_solutions", "Solutions")) +
          "</strong>" +
          '<a href="' +
          esc(chromeUrl("nav_solutions_url", "/solutions")) +
          '"' +
          ed("chrome:nav_solutions") +
          ">" +
          esc(chromeText("nav_solutions", "Solutions")) +
          '</a><a href="' +
          esc(chromeUrl("nav_pricing_url", "/pricing")) +
          '"' +
          ed("chrome:nav_pricing") +
          ">" +
          esc(chromeText("nav_pricing", "Pricing")) +
          '</a><a href="' +
          esc(chromeUrl("nav_templates_url", "#templates")) +
          '"' +
          ed("chrome:nav_templates") +
          ">" +
          esc(chromeText("nav_templates", "Templates")) +
          "</a></div><div><strong" +
          ed("chrome:footer_contact") +
          ">" +
          esc(chromeText("footer_contact", "Contact")) +
          "</strong><a href=\"mailto:" +
          esc(chrome.contact_email || "dev@flexloopers.com") +
          '"' +
          ed("chrome:contact_email") +
          ">" +
          esc(chrome.contact_email || "dev@flexloopers.com") +
          '</a><a href="' +
          esc(chrome.contact_url || "https://flexloopers.com") +
          '"' +
          ed("chrome:contact_url_label") +
          ">" +
          esc(chrome.contact_url_label || "flexloopers.com") +
          "</a></div></div></div>" +
          '<div class="sm-wrap sm-footer-copy">© <span' +
          ed("chrome:copyright_year") +
          ">" +
          esc(chrome.copyright_year || new Date().getFullYear()) +
          "</span> <span" +
          ed("chrome:footer_legal") +
          ">" +
          esc(chromeText("footer_legal", chromeText("footer_copy", ""))) +
          "</span></div></footer></div>"
        );
      }

      function renderSection(block) {
        var p = block.props || {};
        var inner = "";
        if (block.type === "hero") {
          inner =
            '<section class="sm-hero sm-hero--full">' +
            '<div class="' +
            imgHitClass(block.id, "image", "sm-hero-bg") +
            '" data-img-path="image" title="Select image" aria-hidden="true">' +
            (p.image ? '<img class="sm-hero-img" src="' + esc(p.image) + '" alt="">' : "") +
            '<div class="sm-hero-scrim"></div>' +
            '<div class="sm-hero-fx"><span class="sm-hero-beam"></span><span class="sm-hero-dust"></span></div></div>' +
            '<div class="sm-wrap sm-hero-grid"><div class="sm-hero-copy">' +
            (p.brand_mark
              ? '<a class="sm-brand-mark" href="/"' + ed("prop:brand_mark") + ">" + brandHtml(p.brand_mark) + "</a>"
              : "") +
            "<h1" +
            ed("prop:title") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "Hero")) +
            "</h1><p" +
            ed("prop:subtitle") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "subtitle"), lang, "")) +
            '</p><div class="sm-hero-actions">' +
            (p.cta_primary_url
              ? '<a class="sm-btn" href="' +
                esc(p.cta_primary_url) +
                '"' +
                ed("prop:cta_primary_label") +
                ">" +
                esc(resolveI18n(hydrateI18n(p, "cta_primary_label"), lang, "Get started")) +
                "</a>"
              : "") +
            (p.cta_secondary_url
              ? '<a class="sm-btn sm-btn-ghost" href="' +
                esc(p.cta_secondary_url) +
                '"' +
                ed("prop:cta_secondary_label") +
                ">" +
                esc(resolveI18n(hydrateI18n(p, "cta_secondary_label"), lang, "")) +
                "</a>"
              : "") +
            "</div></div></div></section>";
        } else if (block.type === "proof") {
          inner =
            '<section class="sm-proof"><div class="sm-wrap sm-proof-row">' +
            '<span class="sm-proof-line"' +
            ed("prop:line") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "line"), lang, "Proof")) +
            '</span><ul class="sm-proof-stats">' +
            (p.stats || [])
              .map(function (s, i) {
                return "<li" + ed("prop:stats." + i + ".text") + ">" + esc(resolveI18n(s.text_i18n || {}, lang, "")) + "</li>";
              })
              .join("") +
            "</ul></div></section>";
        } else if (block.type === "pillars") {
          inner =
            '<section class="sm-section"><div class="sm-wrap"><div class="sm-section-head"><h2' +
            ed("prop:title") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "")) +
            "</h2><p" +
            ed("prop:subtitle") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "subtitle"), lang, "")) +
            '</p></div><div class="sm-pillars">' +
            (p.items || [])
              .map(function (it, i) {
                var coming = it.badge === "coming";
                var imgPath = "items." + i + ".image";
                var media =
                  '<div class="' +
                  imgHitClass(block.id, imgPath, "sm-pillar-media") +
                  (!it.image ? " sl-ed-img-empty" : "") +
                  '" data-img-path="' +
                  imgPath +
                  '" title="Select image">' +
                  (it.image
                    ? '<img class="sm-pillar-img" src="' + esc(it.image) + '" alt="">'
                    : '<span class="sl-ed-img-placeholder">Click to add image</span>') +
                  '<span class="sm-badge' +
                  (coming ? "" : " sm-badge-ok") +
                  '">' +
                  esc(coming ? chromeText("badge_coming", "Coming soon") : chromeText("badge_available", "Available")) +
                  '</span><span class="sl-ed-img-change">Change</span></div>';
                return (
                  '<article class="sm-pillar' +
                  (coming ? " sm-pillar-soon" : "") +
                  '">' +
                  media +
                  '<div class="sm-pillar-body"><h3' +
                  ed("prop:items." + i + ".title") +
                  ">" +
                  esc(resolveI18n(it.title_i18n || {}, lang, "")) +
                  "</h3><p" +
                  ed("prop:items." + i + ".desc") +
                  ">" +
                  esc(resolveI18n(it.desc_i18n || {}, lang, "")) +
                  "</p></div></article>"
                );
              })
              .join("") +
            "</div>" +
            (p.link_url
              ? '<div class="sm-section-cta"><a class="sm-link" href="' +
                esc(p.link_url) +
                '"><span' +
                ed("prop:link_label") +
                ">" +
                esc(resolveI18n(hydrateI18n(p, "link_label"), lang, "Learn more")) +
                "</span> →</a></div>"
              : "") +
            "</div></section>";
        } else if (block.type === "audience") {
          inner =
            '<section class="sm-section sm-section-alt"><div class="sm-wrap"><div class="sm-section-head"><h2' +
            ed("prop:title") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "")) +
            '</h2></div><div class="sm-audience">' +
            (p.items || [])
              .map(function (it, i) {
                var imgPath = "items." + i + ".image";
                var media =
                  '<div class="' +
                  imgHitClass(block.id, imgPath, "sm-audience-media") +
                  (!it.image ? " sl-ed-img-empty" : "") +
                  '" data-img-path="' +
                  imgPath +
                  '" title="Select image">' +
                  (it.image
                    ? '<img class="sm-audience-img" src="' + esc(it.image) + '" alt="">'
                    : '<span class="sl-ed-img-placeholder">Click to add image</span>') +
                  '<span class="sl-ed-img-change">Change</span></div>';
                return (
                  '<article class="sm-audience-card">' +
                  media +
                  '<div class="sm-audience-body"><h3' +
                  ed("prop:items." + i + ".title") +
                  ">" +
                  esc(resolveI18n(it.title_i18n || {}, lang, "")) +
                  "</h3><p" +
                  ed("prop:items." + i + ".desc") +
                  ">" +
                  esc(resolveI18n(it.desc_i18n || {}, lang, "")) +
                  "</p></div></article>"
                );
              })
              .join("") +
            "</div></div></section>";
        } else if (block.type === "demos") {
          inner =
            '<section class="sm-section" id="templates"><div class="sm-wrap"><div class="sm-section-head"><h2' +
            ed("prop:title") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "Demos")) +
            "</h2><p" +
            ed("prop:subtitle") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "subtitle"), lang, "")) +
            '</p></div><div class="sm-demo-grid">' +
            (p.items || [])
              .map(function (d, i) {
                return (
                  '<a class="sm-demo-card" href="' +
                  esc(d.url || "#") +
                  '" style="--demo-bg: ' +
                  esc(d.color || "#111") +
                  "; --demo-accent: " +
                  esc(d.accent || "#111") +
                  '"><div class="' +
                  imgHitClass(block.id, "items." + i + ".image", "sm-demo-media") +
                  '" data-img-path="items.' +
                  i +
                  '.image" title="Select image">' +
                  (d.image ? '<img class="sm-demo-img" src="' + esc(d.image) + '" alt="">' : "") +
                  '<span class="sm-demo-accent-dot"></span><span class="sl-ed-img-change">Change</span></div><div class="sm-demo-meta"><span class="sm-demo-niche"' +
                  ed("prop:items." + i + ".niche") +
                  ">" +
                  esc(resolveI18n(d.niche_i18n || {}, lang, "")) +
                  "</span><strong" +
                  ed("prop:items." + i + ".name") +
                  ">" +
                  esc(resolveI18n(d.name_i18n || {}, lang, d.key || "")) +
                  '</strong><span class="sm-demo-open"><span' +
                  ed("prop:open_label") +
                  ">" +
                  esc(resolveI18n(hydrateI18n(p, "open_label"), lang, "Open")) +
                  "</span> →</span></div></a>"
                );
              })
              .join("") +
            "</div></div></section>";
        } else if (block.type === "steps") {
          inner =
            '<section class="sm-section sm-section-alt"><div class="sm-wrap"><div class="sm-section-head"><h2' +
            ed("prop:title") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "")) +
            '</h2></div><div class="sm-grid sm-steps">' +
            (p.items || [])
              .map(function (it, i) {
                return (
                  '<div class="sm-card"><span class="sm-step-num">' +
                  (i + 1) +
                  "</span><h3" +
                  ed("prop:items." + i + ".title") +
                  ">" +
                  esc(resolveI18n(it.title_i18n || {}, lang, "")) +
                  "</h3><p" +
                  ed("prop:items." + i + ".desc") +
                  ">" +
                  esc(resolveI18n(it.desc_i18n || {}, lang, "")) +
                  "</p></div>"
                );
              })
              .join("") +
            "</div></div></section>";
        } else if (block.type === "diff") {
          inner =
            '<section class="sm-section"><div class="sm-wrap"><div class="sm-diff">' +
            '<div class="' +
            imgHitClass(block.id, "image", "sm-diff-media") +
            '" data-img-path="image" title="Select image">' +
            (p.image ? '<img class="sm-diff-img" src="' + esc(p.image) + '" alt="">' : "") +
            '</div><div class="sm-diff-copy"><h2' +
            ed("prop:title") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "")) +
            "</h2><p" +
            ed("prop:subtitle") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "subtitle"), lang, "")) +
            "</p></div></div></div></section>";
        } else if (block.type === "cta_banner") {
          var mosaic = "";
          if (p.use_demo_mosaic) {
            mosaic =
              '<div class="sm-banner-mosaic">' +
              demoImages()
                .map(function (src) {
                  return '<img class="sm-banner-tile" src="' + esc(src) + '" alt="">';
                })
                .join("") +
              "</div>";
          }
          inner =
            '<section class="sm-section"><div class="sm-wrap"><div class="sm-banner">' +
            mosaic +
            '<div class="sm-banner-copy"><h2' +
            ed("prop:title") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "")) +
            "</h2><p" +
            ed("prop:subtitle") +
            ">" +
            esc(resolveI18n(hydrateI18n(p, "subtitle"), lang, "")) +
            "</p>" +
            (p.cta_url
              ? '<a class="sm-btn sm-btn-on-dark" href="' +
                esc(p.cta_url) +
                '"' +
                ed("prop:cta_label") +
                ">" +
                esc(resolveI18n(hydrateI18n(p, "cta_label"), lang, "Get started")) +
                "</a>"
              : "") +
            "</div></div></div></section>";
        } else if (block.type === "html") {
          inner = '<section class="sm-section"><div class="sm-wrap">' + (p.html || "<em>HTML</em>") + "</div></section>";
        } else if (block.type === "spacer") {
          inner = '<div style="height:' + esc(p.height || 40) + 'px" aria-hidden="true"></div>';
        } else {
          inner = '<section class="sm-section"><div class="sm-wrap"><p>' + esc(block.type) + "</p></div></section>";
        }
        return wrapSection(block, inner);
      }

      function canvasHtml() {
        if (!blocks.length) {
          return '<div class="sl-ed-empty-canvas">Add a block from the left to start editing the landing page.</div>';
        }
        return renderChromeTop() + blocks.map(renderSection).join("") + renderChromeFooter();
      }

      function i18nField(prefix, label, map) {
        var rows = i18nRowsFromMap(map || {});
        var html =
          '<div class="sl-ed-field"><label>' +
          esc(label) +
          ' <button type="button" class="sl-ed-mini" data-i18n-add="' +
          esc(prefix) +
          '">+ lang</button></label>';
        rows.forEach(function (r, idx) {
          html +=
            '<div class="sl-ed-i18n-row">' +
            '<select class="sl-ed-i18n-lang" data-i18n-lang="' +
            esc(prefix) +
            '" data-idx="' +
            idx +
            '">' +
            I18N_LANGS.map(function (c) {
              return '<option value="' + c + '"' + (c === r.lang ? " selected" : "") + ">" + c + "</option>";
            }).join("") +
            '</select><input class="sl-ed-i18n-val" data-i18n-val="' +
            esc(prefix) +
            '" data-idx="' +
            idx +
            '" lang="' +
            esc(r.lang) +
            '" dir="' +
            (r.lang === "ar" ? "rtl" : "ltr") +
            '" value="' +
            esc(r.value) +
            '">' +
            '<button type="button" class="sl-ed-mini" data-i18n-del="' +
            esc(prefix) +
            '" data-idx="' +
            idx +
            '">×</button></div>';
        });
        html += "</div>";
        return html;
      }

      function field(key, label, val, kind) {
        kind = kind || "text";
        var focus = selectedMedia && selectedMedia.path === key ? " is-img-focus" : "";
        var wrap = ' class="sl-ed-field' + focus + '" data-img-field="' + esc(key) + '"';
        if (kind === "textarea") {
          return (
            "<div" +
            wrap +
            "><label>" +
            esc(label) +
            '</label><textarea data-prop="' +
            esc(key) +
            '">' +
            esc(val || "") +
            "</textarea></div>"
          );
        }
        return (
          "<div" +
          wrap +
          "><label>" +
          esc(label) +
          '</label><input data-prop="' +
          esc(key) +
          '" type="' +
          kind +
          '" value="' +
          esc(val == null ? "" : val) +
          '"></div>'
        );
      }

      function isImgSel(blockId, path) {
        return !!(selectedMedia && selectedMedia.id === blockId && selectedMedia.path === path);
      }

      function imgHitClass(blockId, path, extra) {
        return (
          (extra || "") +
          " sl-ed-img-hit" +
          (isImgSel(blockId, path) ? " is-img-selected" : "")
        );
      }

      function applyI18nPrefix(prefix, map) {
        if (editingChrome()) {
          setDeep(chrome, prefix + "_i18n", map);
          return;
        }
        var b = selectedBlock();
        if (!b) return;
        if (prefix.indexOf("items.") === 0) {
          var m = prefix.match(/^items\.(\d+)\.(title|desc|name|niche)$/);
          if (m) setDeep(b.props, "items." + m[1] + "." + m[2] + "_i18n", map);
        } else if (prefix.indexOf("stats.") === 0) {
          var m2 = prefix.match(/^stats\.(\d+)\.text$/);
          if (m2) setDeep(b.props, "stats." + m2[1] + ".text_i18n", map);
        } else {
          setDeep(b.props, prefix + "_i18n", map);
        }
      }

      function syncI18nHidden(root, prefix) {
        var rows = [];
        root.querySelectorAll('[data-i18n-lang="' + prefix + '"]').forEach(function (sel) {
          var idx = sel.getAttribute("data-idx");
          var inp = root.querySelector('[data-i18n-val="' + prefix + '"][data-idx="' + idx + '"]');
          rows.push({ lang: sel.value, value: inp ? inp.value : "" });
        });
        applyI18nPrefix(prefix, mapFromI18nRows(rows));
      }

      function propsPanelHtml() {
        if (selected === "__header__") {
          return (
            '<p class="sl-ed-panel-title">Header</p>' +
            '<p class="sl-ed-hint">Click any text on the canvas to type, or edit here.</p>' +
            field("brand_mark", "Brand mark", chrome.brand_mark || "Dukan") +
            i18nField("announcement", "Announcement bar", hydrateI18n(chrome, "announcement")) +
            i18nField("nav_solutions", "Nav: Solutions", hydrateI18n(chrome, "nav_solutions")) +
            field("nav_solutions_url", "Solutions URL", chromeUrl("nav_solutions_url", "/solutions")) +
            i18nField("nav_pricing", "Nav: Pricing", hydrateI18n(chrome, "nav_pricing")) +
            field("nav_pricing_url", "Pricing URL", chromeUrl("nav_pricing_url", "/pricing")) +
            i18nField("nav_templates", "Nav: Templates", hydrateI18n(chrome, "nav_templates")) +
            field("nav_templates_url", "Templates URL", chromeUrl("nav_templates_url", "#templates")) +
            i18nField("nav_login", "Nav: Login", hydrateI18n(chrome, "nav_login")) +
            field("nav_login_url", "Login URL", chromeUrl("nav_login_url", "/login")) +
            i18nField("cta_create", "Header CTA label", hydrateI18n(chrome, "cta_create")) +
            field("cta_create_url", "Header CTA URL", chromeUrl("cta_create_url", "/signup"))
          );
        }
        if (selected === "__footer__") {
          return (
            '<p class="sl-ed-panel-title">Footer</p>' +
            '<p class="sl-ed-hint">Click any text on the canvas to type, or edit here.</p>' +
            field("brand_mark", "Brand mark", chrome.brand_mark || "Dukan") +
            i18nField("footer_copy", "Tagline (under logo)", hydrateI18n(chrome, "footer_copy")) +
            field("copyright_year", "Copyright year", chrome.copyright_year || new Date().getFullYear()) +
            i18nField("footer_legal", "Copyright text", hydrateI18n(chrome, "footer_legal")) +
            i18nField("footer_contact", "Contact heading", hydrateI18n(chrome, "footer_contact")) +
            field("contact_email", "Contact email", chrome.contact_email || "") +
            field("contact_url", "Website URL", chrome.contact_url || "") +
            field("contact_url_label", "Website label", chrome.contact_url_label || "")
          );
        }
        var b = selectedBlock();
        if (!b) {
          return (
            '<p class="sl-ed-hint">Select the header, footer, or a block on the canvas. Edits update the live preview immediately. Publish to put them on flexloopers.com.</p>'
          );
        }
        var p = b.props || {};
        var fields = '<p class="sl-ed-panel-title">' + esc(labelOf(catalogItem(b.type), lang) || b.type) + "</p>";
        if (b.type === "hero") {
          fields += field("brand_mark", "Brand mark", p.brand_mark || "");
          fields += i18nField("title", "Title", hydrateI18n(p, "title"));
          fields += i18nField("subtitle", "Subtitle", hydrateI18n(p, "subtitle"));
          fields += field("image", "Background image URL", p.image || "");
          fields += i18nField("cta_primary_label", "Primary CTA label", hydrateI18n(p, "cta_primary_label"));
          fields += field("cta_primary_url", "Primary CTA URL", p.cta_primary_url || "");
          fields += i18nField("cta_secondary_label", "Secondary CTA label", hydrateI18n(p, "cta_secondary_label"));
          fields += field("cta_secondary_url", "Secondary CTA URL", p.cta_secondary_url || "");
        } else if (b.type === "proof") {
          fields += i18nField("line", "Line", hydrateI18n(p, "line"));
          (p.stats || []).forEach(function (s, i) {
            fields +=
              '<h4 class="sl-ed-field-group">Stat ' +
              (i + 1) +
              "</h4>" +
              i18nField("stats." + i + ".text", "Text", s.text_i18n || {});
          });
          fields += '<button type="button" class="sl-btn" data-add-stat="1">+ Add stat</button>';
        } else if (b.type === "pillars" || b.type === "audience" || b.type === "steps") {
          fields += i18nField("title", "Section title", hydrateI18n(p, "title"));
          if (b.type === "pillars") {
            fields += i18nField("subtitle", "Subtitle", hydrateI18n(p, "subtitle"));
            fields += i18nField("link_label", "Link label", hydrateI18n(p, "link_label"));
            fields += field("link_url", "Link URL", p.link_url || "");
          }
          (p.items || []).forEach(function (it, i) {
            fields += '<h4 class="sl-ed-field-group">Item ' + (i + 1) + "</h4>";
            fields += i18nField("items." + i + ".title", "Title", it.title_i18n || {});
            fields += i18nField("items." + i + ".desc", "Description", it.desc_i18n || {});
            if (b.type === "pillars" || b.type === "audience") {
              if (b.type === "pillars") {
                fields +=
                  '<div class="sl-ed-field"><label>Badge</label><select data-prop="items.' +
                  i +
                  '.badge"><option value="available"' +
                  (it.badge !== "coming" ? " selected" : "") +
                  '>Available</option><option value="coming"' +
                  (it.badge === "coming" ? " selected" : "") +
                  ">Coming soon</option></select></div>";
              }
              if (it.image) {
                fields += '<div class="sl-ed-thumb"><img src="' + esc(it.image) + '" alt=""></div>';
              }
              fields += field("items." + i + ".image", "Image URL", it.image || "");
              fields +=
                '<div class="sl-ed-field"><button type="button" class="sl-btn" data-fetch-img="' +
                i +
                '">Fetch image from web</button></div>';
            }
          });
          fields += '<button type="button" class="sl-btn" data-add-item="1">+ Add item</button>';
          if (b.type === "pillars" || b.type === "audience") {
            fields +=
              '<button type="button" class="sl-btn" style="margin-top:0.4rem" data-fetch-all-img="1">Fetch images for all items</button>';
          }
        } else if (b.type === "demos") {
          fields += i18nField("title", "Title", hydrateI18n(p, "title"));
          fields += i18nField("subtitle", "Subtitle", hydrateI18n(p, "subtitle"));
          fields += i18nField("open_label", "Open label", hydrateI18n(p, "open_label"));
          (p.items || []).forEach(function (d, i) {
            var foldKey = b.id + ":demo:" + i;
            var mediaOpen =
              selectedMedia && selectedMedia.id === b.id && selectedMedia.path === "items." + i + ".image";
            var open =
              mediaOpen ||
              (Object.prototype.hasOwnProperty.call(foldState, foldKey) ? foldState[foldKey] : false);
            var demoName = resolveI18n(d.name_i18n || {}, lang, d.key || "");
            fields +=
              '<details class="sl-ed-fold"' +
              (open ? " open" : "") +
              ' data-fold="' +
              esc(foldKey) +
              '"><summary class="sl-ed-fold-sum"><span>Demo ' +
              (i + 1) +
              (demoName ? " · " + esc(demoName) : "") +
              '</span></summary><div class="sl-ed-fold-body">';
            fields += field("items." + i + ".key", "Key / subdomain", d.key || "");
            fields += i18nField("items." + i + ".name", "Name", d.name_i18n || {});
            fields += i18nField("items." + i + ".niche", "Niche", d.niche_i18n || {});
            fields += field("items." + i + ".url", "URL", d.url || "");
            fields += field("items." + i + ".image", "Image URL", d.image || "");
            fields += field("items." + i + ".color", "Color", d.color || "", "color");
            fields += field("items." + i + ".accent", "Accent", d.accent || "", "color");
            fields += "</div></details>";
          });
          fields += '<button type="button" class="sl-btn" data-add-demo="1">+ Add demo</button>';
        } else if (b.type === "diff") {
          fields += i18nField("title", "Title", hydrateI18n(p, "title"));
          fields += i18nField("subtitle", "Subtitle", hydrateI18n(p, "subtitle"));
          fields += field("image", "Image URL", p.image || "");
        } else if (b.type === "cta_banner") {
          fields += i18nField("title", "Title", hydrateI18n(p, "title"));
          fields += i18nField("subtitle", "Subtitle", hydrateI18n(p, "subtitle"));
          fields += i18nField("cta_label", "CTA label", hydrateI18n(p, "cta_label"));
          fields += field("cta_url", "CTA URL", p.cta_url || "");
          fields +=
            '<div class="sl-ed-field"><label><input type="checkbox" data-prop="use_demo_mosaic" value="1"' +
            (p.use_demo_mosaic ? " checked" : "") +
            "> Use demo mosaic background</label></div>";
        } else if (b.type === "html") {
          fields += field("html", "HTML", p.html || "", "textarea");
        } else if (b.type === "spacer") {
          fields += field("height", "Height (px)", p.height || 40, "number");
        }
        return fields;
      }

      function sectionId(sec) {
        if (sec.getAttribute("data-chrome-sel") === "header") return "__header__";
        if (sec.getAttribute("data-chrome-sel") === "footer") return "__footer__";
        return sec.getAttribute("data-id");
      }

      function selectItem(id, opts) {
        opts = opts || {};
        var wrap = host.querySelector(".sl-ed-canvas-wrap");
        var top = wrap ? wrap.scrollTop : 0;
        selected = id;
        if (Object.prototype.hasOwnProperty.call(opts, "mediaPath")) {
          selectedMedia = opts.mediaPath ? { id: id, path: opts.mediaPath } : null;
        } else if (!selectedMedia || selectedMedia.id !== id) {
          selectedMedia = null;
        }
        host.querySelectorAll(".sl-ed-outline [data-sel]").forEach(function (el) {
          el.classList.toggle("is-active", el.getAttribute("data-sel") === id);
        });
        host.querySelectorAll(".sl-ed-section").forEach(function (el) {
          el.classList.toggle("is-selected", sectionId(el) === id);
        });
        host.querySelectorAll("[data-img-path]").forEach(function (el) {
          var sec = el.closest(".sl-ed-section");
          var on =
            !!(selectedMedia && sec && sectionId(sec) === id && el.getAttribute("data-img-path") === selectedMedia.path);
          el.classList.toggle("is-img-selected", on);
        });
        var props = host.querySelector("#sl-ed-props");
        if (props) {
          var pTop = props.scrollTop;
          props.innerHTML = propsPanelHtml();
          bindProps(props);
          if (selectedMedia) {
            var imgField = props.querySelector('[data-img-field="' + selectedMedia.path + '"]');
            if (imgField) {
              imgField.classList.add("is-img-focus");
              imgField.scrollIntoView({ block: "center", inline: "nearest" });
              var inp = imgField.querySelector("input, textarea");
              if (inp) inp.focus();
            }
          } else {
            props.scrollTop = pTop;
          }
        }
        if (wrap) wrap.scrollTop = top;
        if (opts.scrollIntoView) {
          var target = host.querySelector(".sl-ed-img-hit.is-img-selected") || host.querySelector(".sl-ed-section.is-selected");
          if (target && wrap) {
            var wr = wrap.getBoundingClientRect();
            var tr = target.getBoundingClientRect();
            if (tr.top < wr.top + 8 || tr.bottom > wr.bottom - 8) {
              target.scrollIntoView({ block: "nearest", inline: "nearest" });
            }
          }
        }
      }

      function setLangValue(obj, prefix, value) {
        var map = hydrateI18n(obj, prefix);
        map[lang] = value;
        obj[prefix + "_i18n"] = map;
      }

      function applyBindSpec(spec, value, blockId) {
        var parts = String(spec || "").split(":");
        var kind = parts[0];
        var path = parts.slice(1).join(":");
        var plain = { brand_mark: 1, contact_email: 1, contact_url_label: 1, copyright_year: 1 };
        if (kind === "chrome") {
          if (plain[path]) chrome[path] = value;
          else setLangValue(chrome, path, value);
          return;
        }
        var b = blocks.find(function (x) {
          return x.id === blockId;
        });
        if (!b) return;
        if (path === "brand_mark") {
          b.props.brand_mark = value;
          return;
        }
        var m = path.match(/^items\.(\d+)\.(title|desc|name|niche)$/);
        if (m) {
          var item = ((b.props.items || [])[Number(m[1])]) || null;
          if (!item) return;
          var key = m[2] + "_i18n";
          item[key] = Object.assign({}, item[key] || {});
          item[key][lang] = value;
          return;
        }
        var m2 = path.match(/^stats\.(\d+)\.text$/);
        if (m2) {
          var stat = ((b.props.stats || [])[Number(m2[1])]) || null;
          if (!stat) return;
          stat.text_i18n = Object.assign({}, stat.text_i18n || {});
          stat.text_i18n[lang] = value;
          return;
        }
        setLangValue(b.props, path, value);
      }

      function bindInline() {
        host.querySelectorAll("[data-bind]").forEach(function (el) {
          if (el.getAttribute("data-bound") === "1") return;
          el.setAttribute("data-bound", "1");
          el.addEventListener("click", function (e) {
            e.stopPropagation();
            var sec = el.closest(".sl-ed-section");
            var id = sec ? sectionId(sec) : null;
            if (id && selected !== id) selectItem(id, { scrollIntoView: false, mediaPath: null });
            el.focus();
          });
          el.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
              e.preventDefault();
              el.blur();
            }
          });
          el.addEventListener("paste", function (e) {
            e.preventDefault();
            var t = (e.clipboardData || window.clipboardData).getData("text/plain") || "";
            document.execCommand("insertText", false, t.replace(/\s+/g, " ").trim());
          });
          el.addEventListener("input", function () {
            var spec = el.getAttribute("data-bind");
            var sec = el.closest("[data-id], [data-chrome-sel]");
            var blockId = sec && sec.getAttribute("data-id");
            applyBindSpec(spec, (el.innerText || "").replace(/\s+\n/g, " ").trim(), blockId);
            markDirty();
          });
        });
      }

      function bindCanvas() {
        host.querySelectorAll(".sl-ed-section").forEach(function (sec) {
          sec.onclick = function (e) {
            if (e.target.closest("[data-bind]")) return;
            e.preventDefault();
            e.stopPropagation();
            var wrap = host.querySelector(".sl-ed-canvas-wrap");
            var top = wrap ? wrap.scrollTop : 0;
            var id = sectionId(sec);
            if (!id) return;
            var hit = e.target.closest("[data-img-path]");
            selectItem(id, {
              scrollIntoView: false,
              mediaPath: hit ? hit.getAttribute("data-img-path") : null,
            });
            if (wrap) wrap.scrollTop = top;
            requestAnimationFrame(function () {
              if (wrap) wrap.scrollTop = top;
            });
          };
        });
        bindInline();
      }

      function refreshCanvas() {
        if (document.activeElement && document.activeElement.getAttribute("data-bind")) return;
        var wrap = host.querySelector(".sl-ed-canvas-wrap");
        var top = wrap ? wrap.scrollTop : 0;
        var canvas = host.querySelector("#sl-ed-canvas");
        if (!canvas) return;
        canvas.innerHTML = canvasHtml();
        canvas.className = "sl-ed-canvas is-" + viewport;
        bindCanvas();
        if (wrap) wrap.scrollTop = top;
        requestAnimationFrame(function () {
          if (wrap) wrap.scrollTop = top;
        });
      }

      function paint() {
        var scroll = captureScroll();
        var byGroup = {};
        catalog.forEach(function (c) {
          var g = c.group || "other";
          if (!byGroup[g]) byGroup[g] = [];
          byGroup[g].push(c);
        });
        var catalogHtml = Object.keys(groups)
          .map(function (g) {
            var items = byGroup[g] || [];
            if (!items.length) return "";
            return (
              '<div class="sl-ed-group"><h4>' +
              esc(groups[g]) +
              "</h4>" +
              items
                .map(function (c) {
                  return (
                    '<button type="button" class="sl-ed-block-btn" data-add="' +
                    esc(c.type) +
                    '"><span>' +
                    esc(labelOf(c, lang)) +
                    "</span><span>+</span></button>"
                  );
                })
                .join("") +
              "</div>"
            );
          })
          .join("");

        var outline =
          '<ul class="sl-ed-outline">' +
          '<li class="' +
          (selected === "__header__" ? "is-active" : "") +
          ' is-chrome" data-sel="__header__"><span>Header</span><span class="sl-ed-outline-tag">fixed</span></li>' +
          blocks
            .map(function (b) {
              var c = catalogItem(b.type);
              return (
                '<li class="' +
                (selected === b.id ? "is-active" : "") +
                '" data-sel="' +
                esc(b.id) +
                '"><span>' +
                esc(labelOf(c, lang) || b.type) +
                '</span><span class="sl-ed-outline-actions">' +
                '<button type="button" class="sl-ed-mini" data-up="' +
                esc(b.id) +
                '">↑</button>' +
                '<button type="button" class="sl-ed-mini" data-down="' +
                esc(b.id) +
                '">↓</button>' +
                '<button type="button" class="sl-ed-mini" data-del-id="' +
                esc(b.id) +
                '">×</button></span></li>'
              );
            })
            .join("") +
          '<li class="' +
          (selected === "__footer__" ? "is-active" : "") +
          ' is-chrome" data-sel="__footer__"><span>Footer</span><span class="sl-ed-outline-tag">fixed</span></li>' +
          "</ul>";

        host.innerHTML =
          '<div class="sl-editor' +
          (focusCanvas ? " is-focus" : "") +
          '">' +
          '<div class="sl-ed-top">' +
          '<div class="sl-ed-top-start">' +
          '<a class="sl-ed-home sl-btn" href="/?lang=' +
          encodeURIComponent(lang) +
          '" data-home="1" title="Back to homepage">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"></path></svg>' +
          "Home</a>" +
          '<span class="sl-ed-brand">Landing editor</span>' +
          '<span class="sl-ed-meta' +
          (dirty ? "" : " is-saved") +
          '">' +
          (dirty ? "Unsaved changes" : state.last_saved_on ? "Saved" : state.status || "Draft") +
          "</span>" +
          '<span class="sl-badge ' +
          (state.status === "Published" && !dirty ? "done" : "stub") +
          '">' +
          esc(dirty ? "Draft" : state.status || "Draft") +
          "</span>" +
          '<div class="sl-ed-viewport">' +
          '<button type="button" data-vp="sm" title="Mobile"' +
          (viewport === "sm" ? ' class="is-active"' : "") +
          '><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"></rect></svg></button>' +
          '<button type="button" data-vp="md" title="Tablet"' +
          (viewport === "md" ? ' class="is-active"' : "") +
          '><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"></rect></svg></button>' +
          '<button type="button" data-vp="lg" title="Desktop"' +
          (viewport === "lg" ? ' class="is-active"' : "") +
          '><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"></rect></svg></button></div>' +
          '<div class="sl-ed-lang">' +
          I18N_LANGS.map(function (code) {
            return (
              '<button type="button" data-preview-lang="' +
              code +
              '"' +
              (lang === code ? ' class="is-active"' : "") +
              ">" +
              code.toUpperCase() +
              "</button>"
            );
          }).join("") +
          "</div>" +
          '<button type="button" class="sm-mode-toggle" data-sm-mode-toggle title="Dark / light" aria-label="Toggle dark mode">' +
          '<svg class="sm-mode-icon sm-mode-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 14.3A8.5 8.5 0 1 1 9.7 3 7 7 0 0 0 21 14.3z"></path></svg>' +
          '<svg class="sm-mode-icon sm-mode-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"></path></svg>' +
          "</button></div>" +
          '<div class="sl-ed-top-end">' +
          '<button type="button" class="sl-btn" data-focus="1">' +
          (focusCanvas ? "Show panels" : "Focus canvas") +
          "</button>" +
          '<button type="button" class="sl-btn" data-chrome="1">' +
          (showChrome ? "Hide chrome" : "Show chrome") +
          "</button>" +
          '<a class="sl-btn" href="/?landing_preview=1" target="_blank" rel="noopener">Preview</a>' +
          '<button type="button" class="sl-btn" data-reset="1">Reset default</button>' +
          '<button type="button" class="sl-btn" data-save="1">Save draft</button>' +
          '<button type="button" class="sl-btn sl-btn-primary" data-publish="1">Publish</button>' +
          "</div></div>" +
          '<div class="sl-ed-body">' +
          '<aside class="sl-ed-blocks"><h3 class="sl-ed-panel-title">Outline</h3>' +
          outline +
          '<h3 class="sl-ed-panel-title" style="margin-top:1rem">Blocks</h3>' +
          catalogHtml +
          "</aside>" +
          '<div class="sl-ed-canvas-wrap"><div class="sl-ed-canvas is-' +
          viewport +
          '" id="sl-ed-canvas" dir="' +
          (lang === "ar" ? "rtl" : "ltr") +
          '">' +
          canvasHtml() +
          "</div></div>" +
          '<aside class="sl-ed-props" id="sl-ed-props">' +
          propsPanelHtml() +
          "</aside></div></div>";

        bind();
        restoreScroll(scroll);
        if (selectedMedia) {
          var imgField = host.querySelector('#sl-ed-props [data-img-field="' + selectedMedia.path + '"]');
          if (imgField) imgField.scrollIntoView({ block: "center", inline: "nearest" });
        }
      }

      function bindProps(propsRoot) {
        if (!propsRoot) return;
        if (!selectedBlock() && !editingChrome()) return;
        propsRoot.querySelectorAll("details[data-fold]").forEach(function (el) {
          el.addEventListener("toggle", function () {
            foldState[el.getAttribute("data-fold")] = el.open;
          });
        });
        propsRoot.querySelectorAll("[data-prop]").forEach(function (inp) {
          var handler = function () {
            var val = inp.type === "checkbox" ? (inp.checked ? 1 : 0) : inp.value;
            if (inp.type === "number") val = Number(val);
            if (editingChrome()) {
              setDeep(chrome, inp.getAttribute("data-prop"), val);
            } else {
              var b = selectedBlock();
              if (!b) return;
              setDeep(b.props, inp.getAttribute("data-prop"), val);
            }
            markDirty();
            if (inp.tagName === "SELECT" || inp.type === "checkbox") paint();
            else refreshCanvas();
          };
          inp.addEventListener("change", handler);
          inp.addEventListener("input", handler);
        });

        propsRoot.querySelectorAll("[data-i18n-lang],[data-i18n-val]").forEach(function (el) {
          var handler = function () {
            if (el.matches("[data-i18n-lang]")) {
              var idx = el.getAttribute("data-idx");
              var prefix = el.getAttribute("data-i18n-lang");
              var inp = propsRoot.querySelector('[data-i18n-val="' + prefix + '"][data-idx="' + idx + '"]');
              if (inp) {
                inp.setAttribute("lang", el.value);
                inp.setAttribute("dir", el.value === "ar" ? "rtl" : "ltr");
              }
            }
            var fieldPrefix = el.getAttribute("data-i18n-lang") || el.getAttribute("data-i18n-val");
            syncI18nHidden(propsRoot, fieldPrefix);
            markDirty();
            refreshCanvas();
          };
          el.addEventListener("change", handler);
          el.addEventListener("input", handler);
        });

        propsRoot.querySelectorAll("[data-i18n-add]").forEach(function (btn) {
          btn.onclick = function () {
            var prefix = btn.getAttribute("data-i18n-add");
            var map = {};
            if (editingChrome()) {
              map = hydrateI18n(chrome, prefix);
            } else {
              var b = selectedBlock();
              if (!b) return;
              if (prefix.indexOf("items.") === 0) {
                var m = prefix.match(/^items\.(\d+)\.(title|desc|name|niche)$/);
                if (m) {
                  var key = m[2] + "_i18n";
                  map = Object.assign({}, ((b.props.items || [])[Number(m[1])] || {})[key] || {});
                }
              } else if (prefix.indexOf("stats.") === 0) {
                var m2 = prefix.match(/^stats\.(\d+)\.text$/);
                if (m2) map = Object.assign({}, ((b.props.stats || [])[Number(m2[1])] || {}).text_i18n || {});
              } else {
                map = hydrateI18n(b.props, prefix);
              }
            }
            var avail = I18N_LANGS.find(function (c) {
              return !Object.prototype.hasOwnProperty.call(map, c);
            });
            if (!avail) {
              toast("All languages added");
              return;
            }
            map[avail] = "";
            applyI18nPrefix(prefix, map);
            markDirty();
            paint();
          };
        });

        propsRoot.querySelectorAll("[data-i18n-del]").forEach(function (btn) {
          btn.onclick = function () {
            var prefix = btn.getAttribute("data-i18n-del");
            var idx = Number(btn.getAttribute("data-idx"));
            if (!editingChrome() && !selectedBlock()) return;
            var rows = [];
            propsRoot.querySelectorAll('[data-i18n-lang="' + prefix + '"]').forEach(function (sel) {
              var i = Number(sel.getAttribute("data-idx"));
              if (i === idx) return;
              var inp = propsRoot.querySelector('[data-i18n-val="' + prefix + '"][data-idx="' + i + '"]');
              rows.push({ lang: sel.value, value: inp ? inp.value : "" });
            });
            applyI18nPrefix(prefix, mapFromI18nRows(rows));
            markDirty();
            paint();
          };
        });

        var addItem = propsRoot.querySelector("[data-add-item]");
        if (addItem) {
          addItem.onclick = function () {
            var b = selectedBlock();
            if (!b) return;
            b.props.items = b.props.items || [];
            b.props.items.push({ title_i18n: { en: "" }, desc_i18n: { en: "" }, badge: "available", image: "" });
            markDirty();
            paint();
          };
        }

        async function fetchImageForItem(b, i, btn) {
          var item = (b.props.items || [])[i];
          if (!item) return;
          var title = resolveI18n(item.title_i18n || {}, lang, "online store") || "online store";
          if (btn) {
            btn.disabled = true;
            btn.textContent = "Fetching…";
          }
          try {
            var res = await call("saas_master.api.marketing_editor.fetch_stock_image", { query: title });
            var imgs = (res && res.images) || [];
            if (!imgs.length) {
              toast("No images found");
              return;
            }
            var hostPick = btn ? btn.parentNode : null;
            if (hostPick && imgs.length > 1) {
              var old = hostPick.querySelector(".sl-ed-img-pick");
              if (old) old.remove();
              var box = document.createElement("div");
              box.className = "sl-ed-img-pick";
              imgs.forEach(function (im) {
                var thumb = document.createElement("button");
                thumb.type = "button";
                thumb.className = "sl-ed-img-choice";
                thumb.innerHTML = '<img src="' + esc(im.thumb || im.url) + '" alt="">';
                thumb.onclick = function () {
                  item.image = im.url;
                  markDirty();
                  paint();
                };
                box.appendChild(thumb);
              });
              hostPick.appendChild(box);
              return;
            }
            item.image = imgs[0].url;
            markDirty();
            paint();
          } catch (e) {
            toast(String(e.message || e));
          } finally {
            if (btn) {
              btn.disabled = false;
              btn.textContent = "Fetch image from web";
            }
          }
        }

        propsRoot.querySelectorAll("[data-fetch-img]").forEach(function (btn) {
          btn.onclick = function () {
            var b = selectedBlock();
            if (!b) return;
            fetchImageForItem(b, Number(btn.getAttribute("data-fetch-img")), btn);
          };
        });
        var fetchAll = propsRoot.querySelector("[data-fetch-all-img]");
        if (fetchAll) {
          fetchAll.onclick = async function () {
            var b = selectedBlock();
            if (!b) return;
            fetchAll.disabled = true;
            fetchAll.textContent = "Fetching…";
            try {
              var items = b.props.items || [];
              for (var i = 0; i < items.length; i++) {
                if (items[i] && items[i].image) continue;
                var title = resolveI18n((items[i] && items[i].title_i18n) || {}, lang, "online store");
                var res = await call("saas_master.api.marketing_editor.fetch_stock_image", { query: title });
                var imgs = (res && res.images) || [];
                if (imgs[0] && items[i]) items[i].image = imgs[0].url;
              }
              markDirty();
              paint();
              toast("Images added");
            } catch (e) {
              toast(String(e.message || e));
            } finally {
              fetchAll.disabled = false;
              fetchAll.textContent = "Fetch images for all items";
            }
          };
        }
        var addStat = propsRoot.querySelector("[data-add-stat]");
        if (addStat) {
          addStat.onclick = function () {
            var b = selectedBlock();
            if (!b) return;
            b.props.stats = b.props.stats || [];
            b.props.stats.push({ text_i18n: { en: "" } });
            markDirty();
            paint();
          };
        }
        var addDemo = propsRoot.querySelector("[data-add-demo]");
        if (addDemo) {
          addDemo.onclick = function () {
            var b = selectedBlock();
            if (!b) return;
            b.props.items = b.props.items || [];
            b.props.items.push({
              key: "store",
              name_i18n: { en: "Store" },
              niche_i18n: { en: "Niche" },
              url: "https://store.flexloopers.com/",
              image: "",
              color: "#111111",
              accent: "#111111",
            });
            foldState[b.id + ":demo:" + (b.props.items.length - 1)] = true;
            markDirty();
            paint();
          };
        }
      }

      function bind() {
        host.querySelectorAll("[data-add]").forEach(function (btn) {
          btn.onclick = function () {
            addBlock(btn.getAttribute("data-add"));
          };
        });
        host.querySelectorAll("[data-sel]").forEach(function (el) {
          el.onclick = function (e) {
            if (e.target.closest("[data-up],[data-down],[data-del-id]")) return;
            selectItem(el.getAttribute("data-sel"), { scrollIntoView: true, mediaPath: null });
          };
        });
        host.querySelectorAll("[data-up]").forEach(function (btn) {
          btn.onclick = function (e) {
            e.stopPropagation();
            moveBlock(btn.getAttribute("data-up"), -1);
          };
        });
        host.querySelectorAll("[data-down]").forEach(function (btn) {
          btn.onclick = function (e) {
            e.stopPropagation();
            moveBlock(btn.getAttribute("data-down"), 1);
          };
        });
        host.querySelectorAll("[data-del-id]").forEach(function (btn) {
          btn.onclick = function (e) {
            e.stopPropagation();
            removeBlock(btn.getAttribute("data-del-id"));
          };
        });
        host.querySelectorAll("[data-vp]").forEach(function (btn) {
          btn.onclick = function () {
            viewport = btn.getAttribute("data-vp");
            paint();
          };
        });
        host.querySelectorAll("[data-preview-lang]").forEach(function (btn) {
          btn.onclick = function () {
            lang = btn.getAttribute("data-preview-lang");
            paint();
          };
        });
        var chromeBtn = host.querySelector("[data-chrome]");
        if (chromeBtn) {
          chromeBtn.onclick = function () {
            showChrome = !showChrome;
            paint();
          };
        }
        var focusBtn = host.querySelector("[data-focus]");
        if (focusBtn) {
          focusBtn.onclick = function () {
            focusCanvas = !focusCanvas;
            paint();
          };
        }
        var homeLink = host.querySelector("[data-home]");
        if (homeLink) {
          homeLink.onclick = function (e) {
            if (dirty && !confirm("You have unsaved changes. Leave the editor?")) {
              e.preventDefault();
              return;
            }
            allowLeave = true;
          };
        }

        bindCanvas();
        bindProps(host.querySelector("#sl-ed-props"));

        var saveBtn = host.querySelector("[data-save]");
        if (saveBtn) {
          saveBtn.onclick = async function () {
            try {
              await call("saas_master.api.marketing_editor.save_draft", { blocks: blocks, chrome: chrome });
              dirty = false;
              state.status = "Draft";
              state.last_saved_on = new Date().toISOString();
              toast("Draft saved");
              paint();
            } catch (e) {
              toast(String(e.message || e));
            }
          };
        }
        var pubBtn = host.querySelector("[data-publish]");
        if (pubBtn) {
          pubBtn.onclick = async function () {
            try {
              await call("saas_master.api.marketing_editor.publish", { blocks: blocks, chrome: chrome });
              dirty = false;
              state.status = "Published";
              state.last_saved_on = new Date().toISOString();
              toast("Published — live on the homepage");
              paint();
            } catch (e) {
              toast(String(e.message || e));
            }
          };
        }
        var resetBtn = host.querySelector("[data-reset]");
        if (resetBtn) {
          resetBtn.onclick = async function () {
            if (!confirm("Reset landing to the default Dukan layout?")) return;
            try {
              var res = await call("saas_master.api.marketing_editor.reset_to_default", {});
              blocks = res.draft_blocks || [];
              if (res.chrome) chrome = res.chrome;
              selected = blocks[0] ? blocks[0].id : "__header__";
              dirty = false;
              state.status = res.status || "Published";
              toast("Reset to default");
              paint();
            } catch (e) {
              toast(String(e.message || e));
            }
          };
        }
      }

      paint();
    },
  };
})();
