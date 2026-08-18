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

  window.MarketingEditor = {
    async mount(host, opts) {
      var call = opts.call;
      var toast = opts.toast || alert;
      var lang = opts.lang || "en";

      host.innerHTML = '<p class="sl-loading" style="padding:2rem">Loading editor…</p>';
      var state = await call("saas_master.api.marketing_editor.get_page", {});
      var blocks = Array.isArray(state.draft_blocks) ? state.draft_blocks.slice() : [];
      var selected = blocks[0] ? blocks[0].id : null;
      var viewport = "lg";
      var dirty = false;
      var catalog = state.catalog || [];

      var groups = {
        layout: "Layout",
        content: "Content",
        interaction: "Interaction",
        advanced: "Advanced",
        other: "Other",
      };

      function markDirty() {
        dirty = true;
        var el = host.querySelector(".sl-ed-meta");
        if (el) {
          el.textContent = "Unsaved changes";
          el.classList.remove("is-saved");
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
            '<div class="sl-ed-i18n-row" style="display:flex;gap:.35rem;margin-bottom:.35rem">' +
            '<select data-i18n-lang="' +
            esc(prefix) +
            '" data-idx="' +
            idx +
            '">' +
            I18N_LANGS.map(function (c) {
              return '<option value="' + c + '"' + (c === r.lang ? " selected" : "") + ">" + c + "</option>";
            }).join("") +
            '</select><input style="flex:1" data-i18n-val="' +
            esc(prefix) +
            '" data-idx="' +
            idx +
            '" value="' +
            esc(r.value) +
            '">' +
            '<button type="button" class="sl-ed-mini" data-i18n-del="' +
            esc(prefix) +
            '" data-idx="' +
            idx +
            '">×</button></div>';
        });
        html +=
          '<input type="hidden" data-prop="' +
          esc(prefix + "_i18n") +
          '" data-i18n-json="' +
          esc(prefix) +
          '" value="">';
        html += "</div>";
        return html;
      }

      function syncI18nHidden(root, prefix) {
        var rows = [];
        root.querySelectorAll('[data-i18n-lang="' + prefix + '"]').forEach(function (sel) {
          var idx = sel.getAttribute("data-idx");
          var inp = root.querySelector('[data-i18n-val="' + prefix + '"][data-idx="' + idx + '"]');
          rows.push({ lang: sel.value, value: inp ? inp.value : "" });
        });
        var hidden = root.querySelector('[data-i18n-json="' + prefix + '"]');
        if (hidden) {
          var map = mapFromI18nRows(rows);
          hidden.value = JSON.stringify(map);
          setDeep(selectedBlock().props, prefix + "_i18n", map);
        }
      }

      function field(key, label, val, kind) {
        kind = kind || "text";
        if (kind === "textarea") {
          return (
            '<div class="sl-ed-field"><label>' +
            esc(label) +
            '</label><textarea data-prop="' +
            esc(key) +
            '">' +
            esc(val || "") +
            "</textarea></div>"
          );
        }
        return (
          '<div class="sl-ed-field"><label>' +
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

      function renderSection(block) {
        var c = catalogItem(block.type);
        var label = labelOf(c, lang) || block.type;
        var p = block.props || {};
        var inner = "";
        if (block.type === "hero") {
          var bg = p.image ? "background-image:url('" + esc(p.image) + "')" : "";
          inner =
            '<div class="sl-ed-hero" style="' +
            bg +
            '"><div><h2>' +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "Hero")) +
            "</h2><p>" +
            esc(resolveI18n(hydrateI18n(p, "subtitle"), lang, "")) +
            "</p></div></div>";
        } else if (block.type === "proof") {
          inner =
            "<div><strong>" +
            esc(resolveI18n(hydrateI18n(p, "line"), lang, "Proof")) +
            "</strong><ul>" +
            (p.stats || [])
              .map(function (s) {
                return "<li>" + esc(resolveI18n(s.text_i18n || {}, lang, "")) + "</li>";
              })
              .join("") +
            "</ul></div>";
        } else if (block.type === "demos") {
          inner =
            "<div><h3>" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, "Demos")) +
            '</h3><div class="sl-ed-grid">' +
            (p.items || [])
              .map(function (d) {
                return (
                  '<div class="sl-ed-card">' +
                  (d.image ? '<img src="' + esc(d.image) + '" alt="">' : "") +
                  "<span>" +
                  esc(resolveI18n(d.name_i18n || {}, lang, d.key || "")) +
                  "</span></div>"
                );
              })
              .join("") +
            "</div></div>";
        } else if (block.type === "pillars" || block.type === "audience" || block.type === "steps") {
          inner =
            "<div><h3>" +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, label)) +
            "</h3><ol>" +
            (p.items || [])
              .map(function (it) {
                return (
                  "<li><strong>" +
                  esc(resolveI18n(it.title_i18n || {}, lang, "")) +
                  "</strong> — " +
                  esc(resolveI18n(it.desc_i18n || {}, lang, "")) +
                  "</li>"
                );
              })
              .join("") +
            "</ol></div>";
        } else if (block.type === "diff" || block.type === "cta_banner") {
          var bg2 = p.image ? "background-image:url('" + esc(p.image) + "')" : "";
          inner =
            '<div class="sl-ed-hero" style="' +
            bg2 +
            '"><div><h2>' +
            esc(resolveI18n(hydrateI18n(p, "title"), lang, label)) +
            "</h2><p>" +
            esc(resolveI18n(hydrateI18n(p, "subtitle"), lang, "")) +
            "</p></div></div>";
        } else if (block.type === "html") {
          inner = '<div class="sl-ed-html">' + (p.html || "<em>HTML</em>") + "</div>";
        } else if (block.type === "spacer") {
          inner = '<div class="sl-ed-spacer" style="height:' + esc(p.height || 40) + 'px;background:#f3f4f6"></div>';
        } else {
          inner = "<p>" + esc(block.type) + "</p>";
        }
        return (
          '<section class="sl-ed-section' +
          (selected === block.id ? " is-selected" : "") +
          '" data-id="' +
          esc(block.id) +
          '"><span class="sl-ed-section-badge">' +
          esc(label) +
          "</span>" +
          inner +
          "</section>"
        );
      }

      function propsPanelHtml() {
        var b = selectedBlock();
        if (!b) return "<p style='color:#9ca3af'>Select a block to edit</p>";
        var p = b.props || {};
        var fields = "";
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
          fields +=
            '<button type="button" class="sl-ed-btn" data-add-stat="1">+ Add stat</button>';
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
          });
          fields +=
            '<button type="button" class="sl-ed-btn" data-add-item="1">+ Add item</button>';
        } else if (b.type === "demos") {
          fields += i18nField("title", "Title", hydrateI18n(p, "title"));
          fields += i18nField("subtitle", "Subtitle", hydrateI18n(p, "subtitle"));
          fields += i18nField("open_label", "Open label", hydrateI18n(p, "open_label"));
          (p.items || []).forEach(function (d, i) {
            fields += '<h4 class="sl-ed-field-group">Demo ' + (i + 1) + "</h4>";
            fields += field("items." + i + ".key", "Key / subdomain", d.key || "");
            fields += i18nField("items." + i + ".name", "Name", d.name_i18n || {});
            fields += i18nField("items." + i + ".niche", "Niche", d.niche_i18n || {});
            fields += field("items." + i + ".url", "URL", d.url || "");
            fields += field("items." + i + ".image", "Image URL", d.image || "");
            fields += field("items." + i + ".color", "Color", d.color || "", "color");
            fields += field("items." + i + ".accent", "Accent", d.accent || "", "color");
          });
          fields +=
            '<button type="button" class="sl-ed-btn" data-add-demo="1">+ Add demo</button>';
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

      function paint() {
        var byGroup = {};
        catalog.forEach(function (c) {
          var g = c.group || "other";
          if (!byGroup[g]) byGroup[g] = [];
          byGroup[g].push(c);
        });
        var catalogHtml = Object.keys(byGroup)
          .map(function (g) {
            return (
              "<div class='sl-ed-cat-group'><h4>" +
              esc(groups[g] || g) +
              "</h4>" +
              byGroup[g]
                .map(function (c) {
                  return (
                    '<button type="button" class="sl-ed-add" data-type="' +
                    esc(c.type) +
                    '">' +
                    esc(labelOf(c, lang)) +
                    "</button>"
                  );
                })
                .join("") +
              "</div>"
            );
          })
          .join("");

        var outline = blocks
          .map(function (b, i) {
            var c = catalogItem(b.type);
            return (
              '<div class="sl-ed-outline-item' +
              (selected === b.id ? " is-active" : "") +
              '" data-id="' +
              esc(b.id) +
              '"><span>' +
              (i + 1) +
              ". " +
              esc(labelOf(c, lang) || b.type) +
              '</span><span class="sl-ed-outline-actions">' +
              '<button type="button" data-up="' +
              esc(b.id) +
              '">↑</button>' +
              '<button type="button" data-down="' +
              esc(b.id) +
              '">↓</button>' +
              '<button type="button" data-del="' +
              esc(b.id) +
              '">×</button></span></div>'
            );
          })
          .join("");

        host.innerHTML =
          '<div class="sl-editor">' +
          '<div class="sl-ed-top">' +
          '<div class="sl-ed-top-start"><strong>Landing editor</strong>' +
          '<span class="sl-ed-meta' +
          (dirty ? "" : " is-saved") +
          '">' +
          (dirty ? "Unsaved changes" : state.status === "Published" ? "Published" : "Draft") +
          "</span>" +
          '<div class="sl-ed-viewport">' +
          '<button type="button" data-vp="sm"' +
          (viewport === "sm" ? ' class="is-on"' : "") +
          ">SM</button>" +
          '<button type="button" data-vp="md"' +
          (viewport === "md" ? ' class="is-on"' : "") +
          ">MD</button>" +
          '<button type="button" data-vp="lg"' +
          (viewport === "lg" ? ' class="is-on"' : "") +
          ">LG</button></div></div>" +
          '<div class="sl-ed-top-end">' +
          '<a class="sl-ed-btn" href="/?landing_preview=1" target="_blank" rel="noopener">Preview</a>' +
          '<button type="button" class="sl-ed-btn" data-reset="1">Reset default</button>' +
          '<button type="button" class="sl-ed-btn" data-save="1">Save draft</button>' +
          '<button type="button" class="sl-ed-btn sl-ed-btn-primary" data-publish="1">Publish</button>' +
          "</div></div>" +
          '<div class="sl-ed-body">' +
          '<aside class="sl-ed-left">' +
          "<h3>Blocks</h3>" +
          catalogHtml +
          "<h3>Outline</h3>" +
          '<div class="sl-ed-outline">' +
          outline +
          "</div></aside>" +
          '<main class="sl-ed-canvas-wrap"><div class="sl-ed-canvas is-' +
          viewport +
          '">' +
          blocks.map(renderSection).join("") +
          "</div></main>" +
          '<aside class="sl-ed-right"><h3>Properties</h3><div class="sl-ed-props">' +
          propsPanelHtml() +
          "</div></aside>" +
          "</div></div>";

        bind();
      }

      function bind() {
        host.querySelectorAll("[data-type]").forEach(function (btn) {
          btn.onclick = function () {
            addBlock(btn.getAttribute("data-type"));
          };
        });
        host.querySelectorAll(".sl-ed-outline-item").forEach(function (el) {
          el.onclick = function (e) {
            if (e.target.closest("[data-up],[data-down],[data-del]")) return;
            selected = el.getAttribute("data-id");
            paint();
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
        host.querySelectorAll("[data-del]").forEach(function (btn) {
          btn.onclick = function (e) {
            e.stopPropagation();
            removeBlock(btn.getAttribute("data-del"));
          };
        });
        host.querySelectorAll(".sl-ed-section").forEach(function (sec) {
          sec.onclick = function () {
            selected = sec.getAttribute("data-id");
            paint();
          };
        });
        host.querySelectorAll("[data-vp]").forEach(function (btn) {
          btn.onclick = function () {
            viewport = btn.getAttribute("data-vp");
            paint();
          };
        });

        var propsRoot = host.querySelector(".sl-ed-props");
        if (propsRoot && selectedBlock()) {
          propsRoot.querySelectorAll("[data-prop]").forEach(function (inp) {
            var handler = function () {
              var b = selectedBlock();
              if (!b) return;
              var path = inp.getAttribute("data-prop");
              var val = inp.type === "checkbox" ? (inp.checked ? 1 : 0) : inp.value;
              if (inp.type === "number") val = Number(val);
              if (inp.hasAttribute("data-i18n-json")) {
                try {
                  val = JSON.parse(inp.value || "{}");
                } catch (e) {
                  val = {};
                }
              }
              setDeep(b.props, path, val);
              markDirty();
              if (inp.tagName === "SELECT" || inp.hasAttribute("data-repaint")) paint();
              else {
                // light refresh canvas only for simple fields
              }
            };
            inp.addEventListener("change", handler);
            inp.addEventListener("input", handler);
          });

          // i18n row handlers
          ["title", "subtitle", "line", "cta_primary_label", "cta_secondary_label", "link_label", "open_label", "cta_label"].forEach(
            function (prefix) {
              // also nested prefixes handled via attribute value containing dots
            }
          );
          propsRoot.querySelectorAll("[data-i18n-lang],[data-i18n-val]").forEach(function (el) {
            el.addEventListener("change", function () {
              var prefix = el.getAttribute("data-i18n-lang") || el.getAttribute("data-i18n-val");
              syncI18nHidden(propsRoot, prefix);
              markDirty();
            });
            el.addEventListener("input", function () {
              var prefix = el.getAttribute("data-i18n-val");
              if (prefix) {
                syncI18nHidden(propsRoot, prefix);
                markDirty();
              }
            });
          });
          propsRoot.querySelectorAll("[data-i18n-add]").forEach(function (btn) {
            btn.onclick = function () {
              var prefix = btn.getAttribute("data-i18n-add");
              var b = selectedBlock();
              if (!b) return;
              var path = prefix.indexOf(".") >= 0 ? prefix.replace(/\.(\w+)$/, ".$1_i18n").replace(/^(items\.\d+)\.(title|desc|name|niche|text)$/, "$1.$2_i18n") : prefix + "_i18n";
              // simpler: read current via hydrate based on prefix shape
              var map = {};
              if (prefix.indexOf("items.") === 0) {
                var m = prefix.match(/^items\.(\d+)\.(title|desc|name|niche|text)$/);
                if (m) {
                  var key = m[2] + "_i18n";
                  map = Object.assign({}, ((b.props.items || [])[Number(m[1])] || {})[key] || {});
                  map[I18N_LANGS.find(function (c) {
                    return !map[c];
                  }) || "en"] = "";
                  setDeep(b.props, "items." + m[1] + "." + key, map);
                }
              } else if (prefix.indexOf("stats.") === 0) {
                var m2 = prefix.match(/^stats\.(\d+)\.text$/);
                if (m2) {
                  map = Object.assign({}, ((b.props.stats || [])[Number(m2[1])] || {}).text_i18n || {});
                  map[I18N_LANGS.find(function (c) {
                    return !map[c];
                  }) || "en"] = "";
                  setDeep(b.props, "stats." + m2[1] + ".text_i18n", map);
                }
              } else {
                map = hydrateI18n(b.props, prefix);
                map[I18N_LANGS.find(function (c) {
                  return !map[c];
                }) || "en"] = "";
                setDeep(b.props, prefix + "_i18n", map);
              }
              markDirty();
              paint();
            };
          });
          propsRoot.querySelectorAll("[data-i18n-del]").forEach(function (btn) {
            btn.onclick = function () {
              var prefix = btn.getAttribute("data-i18n-del");
              var idx = Number(btn.getAttribute("data-idx"));
              syncI18nHidden(propsRoot, prefix);
              var b = selectedBlock();
              if (!b) return;
              // rebuild without idx
              var rows = [];
              propsRoot.querySelectorAll('[data-i18n-lang="' + prefix + '"]').forEach(function (sel) {
                var i = Number(sel.getAttribute("data-idx"));
                if (i === idx) return;
                var inp = propsRoot.querySelector('[data-i18n-val="' + prefix + '"][data-idx="' + i + '"]');
                rows.push({ lang: sel.value, value: inp ? inp.value : "" });
              });
              var map = mapFromI18nRows(rows);
              if (prefix.indexOf("items.") === 0) {
                var m = prefix.match(/^items\.(\d+)\.(title|desc|name|niche)$/);
                if (m) setDeep(b.props, "items." + m[1] + "." + m[2] + "_i18n", map);
              } else if (prefix.indexOf("stats.") === 0) {
                var m2 = prefix.match(/^stats\.(\d+)\.text$/);
                if (m2) setDeep(b.props, "stats." + m2[1] + ".text_i18n", map);
              } else setDeep(b.props, prefix + "_i18n", map);
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
              b.props.items.push({
                title_i18n: { en: "" },
                desc_i18n: { en: "" },
                badge: "available",
              });
              markDirty();
              paint();
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
              markDirty();
              paint();
            };
          }
        }

        var saveBtn = host.querySelector("[data-save]");
        if (saveBtn) {
          saveBtn.onclick = async function () {
            try {
              await call("saas_master.api.marketing_editor.save_draft", { blocks: blocks });
              dirty = false;
              state.status = "Draft";
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
              await call("saas_master.api.marketing_editor.publish", { blocks: blocks });
              dirty = false;
              state.status = "Published";
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
              selected = blocks[0] ? blocks[0].id : null;
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

      // Fix i18nField for nested paths: store prefix as full path key for stats/items
      var _i18nField = i18nField;
      i18nField = function (prefix, label, map) {
        // For nested like items.0.title we still use data-i18n-* = prefix and sync writes to items.0.title_i18n
        var rows = i18nRowsFromMap(map || {});
        var html =
          '<div class="sl-ed-field"><label>' +
          esc(label) +
          ' <button type="button" class="sl-ed-mini" data-i18n-add="' +
          esc(prefix) +
          '">+ lang</button></label>';
        rows.forEach(function (r, idx) {
          html +=
            '<div style="display:flex;gap:.35rem;margin-bottom:.35rem">' +
            '<select data-i18n-lang="' +
            esc(prefix) +
            '" data-idx="' +
            idx +
            '">' +
            I18N_LANGS.map(function (c) {
              return '<option value="' + c + '"' + (c === r.lang ? " selected" : "") + ">" + c + "</option>";
            }).join("") +
            '</select><input style="flex:1" data-i18n-val="' +
            esc(prefix) +
            '" data-idx="' +
            idx +
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
      };

      // Override sync to handle nested prefixes
      syncI18nHidden = function (root, prefix) {
        var rows = [];
        root.querySelectorAll('[data-i18n-lang="' + prefix + '"]').forEach(function (sel) {
          var idx = sel.getAttribute("data-idx");
          var inp = root.querySelector('[data-i18n-val="' + prefix + '"][data-idx="' + idx + '"]');
          rows.push({ lang: sel.value, value: inp ? inp.value : "" });
        });
        var map = mapFromI18nRows(rows);
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
      };

      paint();
    },
  };
})();
