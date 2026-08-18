# Dukan vs Zid vs Salla — Competitive Gap Analysis

Living tracker for product and marketing gaps. Update **Status** and the **Progress log** as work ships.

**Last updated:** 2026-08-03  
**Primary market languages (master marketing):** AR · EN · TR

---

## 1. Executive summary

| Platform | Positioning |
|----------|-------------|
| **[Zid](https://zid.sa/ar/)** | Arabic-first KSA commerce OS: store builder, POS (كاشير), payments, shipping network, 400+ apps, themes, financing, marketing, multi-channel (Amazon/TikTok). Strong social proof and pricing page. |
| **[Salla](https://salla.com/)** | Leading Saudi store builder: native payments (Mada, STC, BNPL), 200+ shipping, POS (Salla Point), apps marketplace, Mahally marketplace, ZATCA compliance. |
| **Dukan (us)** | Self-serve multi-tenant SaaS on **ERPNext**: niche templates, guest checkout, real inventory/accounting/returns, TR/EN/AR storefront RTL. Marketing site was thin (EN-only). |

**Our edge:** Real ERP back office (stock, DN/SI, VAT-ready books) — not a lightweight store CMS.  
**Their edge:** Local payment/shipping ecosystems, POS, apps marketplaces, Arabic-first marketing, plan billing, merchant stories.

### Research sources

| Page | Method | Date |
|------|--------|------|
| https://zid.sa/ar/ | **Browser-verified** | 2026-08-03 |
| https://zid.sa/ar/pricing/ | **Browser-verified** | 2026-08-03 |
| https://salla.com/ | **Browser-verified** (after Cloudflare unlock) — nav: Solutions / Resources / Sectors / Special / Pricing; hero “سلة.. تجارة ذكيَّة وسهلة”; pillars payments/shipping/marketing; Mahally; apps 550+ | 2026-08-03 |

---

## 2. Sitemap comparison

| Area | Zid | Salla | Dukan today | Dukan target (P0+) |
|------|-----|-------|-------------|---------------------|
| Home | Rich AR landing | Rich AR landing | AR/EN/TR marketing landing | Keep iterating CTAs/stories |
| Solutions / products | Mega-nav (store, POS, pay, ship, apps, themes, …) | Pillars + Special | `/solutions` stubs | Deep pages per pillar |
| Pricing | Full plans + compare | Plans / Special | `/pricing` roadmap stubs | Real billing later |
| Signup | Create store | Create store | `/signup` wizard | Keep + link from CTAs |
| Demo stores | Demo store CTA | — | 4 niche ports | Template gallery on home |
| Blog / academy | Yes | Yes | No | Later (P2+) |
| Help center | Yes | Yes | No | Later |

---

## 3. Feature matrix

Status: `todo` · `in_progress` · `done` · `wont_do`

| Area | Zid | Salla | Dukan | Severity | Status | Phase | Notes |
|------|-----|-------|-------|----------|--------|-------|-------|
| Online storefront | Yes | Yes | Yes | — | done | — | Guest cart, variants, themes packs |
| Niche / industry templates | Themes | Themes | 4 Site Templates + UI packs | Low | done | — | Fashion / Electronics / Beauty / Home |
| Self-serve signup | Yes | Yes | Yes | — | done | — | 5-step wizard |
| Multi-language storefront | AR+ | AR-first | TR/EN/AR RTL | Low | done | — | |
| Master marketing AR/EN/TR | AR/EN | AR/EN | AR/EN/TR landing | High | done | P0 | Cookie + ?lang= switcher |
| Pricing page | Yes | Yes | Stub roadmap | Medium | done | P0 | No billing backend yet |
| Solutions sitemap | Yes | Yes | Stub | Medium | done | P0 | |
| Real payment gateways | Zid Pay, BNPL | Mada, STC, Tabby, Tamara | COD + mock | Critical | todo | P1 | |
| Carrier shipping / labels | 20+ | 200+ | Flat rate | Critical | todo | P2 | |
| POS / cashier | Zid Cashier | Salla Point | No | High | todo | P3 | ERPNext POS possible later |
| Apps marketplace | 400+ | 550+ | No | High | todo | P3 | |
| Themes marketplace | Yes | Yes | Operator templates only | Medium | todo | P2 | |
| Marketing automation | Yes | Ads, abandoned cart | Coupons only | High | todo | P2 | |
| Custom domain / DNS | Yes | Yes | “Later” in signup | High | todo | P1 | |
| Billing / subscriptions | Paid plans | Paid plans | Free beta | High | todo | P1 | |
| Merchant stories / metrics | Strong | Strong | Honest beta copy | Medium | done | P0 | No fake scale numbers |
| Returns workflow | Yes | Yes | Yes | — | done | — | Return Request |
| Inventory / warehouses | Yes | Yes | ERPNext native | — | done | — | Differentiator |
| Accounting / invoicing | Light | ZATCA / ERP integrations | ERPNext SI/VAT | — | done | — | Differentiator |
| Financing / BNPL | Yes | Tabby/Tamara | No | Medium | todo | P3 | |
| Multi-channel (Amazon, TikTok) | Yes | Mahally + channels | No | Medium | todo | P3 | |
| WhatsApp commerce | Yes (pricing) | Common | Footer link only | Medium | todo | P2 | |
| Merchant dashboard UX | Polished | Polished | Thin `/store-dashboard` + Desk | High | todo | P1 | |

---

## 4. Roadmap phases

### P0 — Marketing + clarity (this sprint)
- [x] Gap analysis MD (this file)
- [x] Redesign master landing (AR/EN/TR)
- [x] `/solutions` and `/pricing` stubs
- [x] Browser verify master + demos; Salla unlocked & verified

### P1 — Trust & money
- Real PSP (Tap / iyzico / Mada path)
- Domain connect docs + automation where possible
- Merchant console polish
- Optional billing / plan flags (even if still free)

### P2 — Operations & growth
- Carrier shipping integrations / label print
- Abandoned cart + WhatsApp/SMS hooks
- Theme gallery UX for merchants
- Help / docs lite

### P3 — Commerce OS parity
- POS (ERPNext POS or dedicated)
- Apps marketplace (or curated integrations hub)
- BNPL partners
- Multi-channel / marketplace listing

---

## 5. Progress log

| Date | Change |
|------|--------|
| 2026-08-03 | Created tracker. Browser-verified Zid home + pricing. Salla.com initially Cloudflare-blocked. |
| 2026-08-03 | P0 shipped: AR/EN/TR landing, `/solutions`, `/pricing`, marketing i18n. Browser-verified master :80 (EN/AR RTL/TR), stubs, demos :8001–:8004. Salla.com browser-verified after unlock. |
