"""Shared AR / EN / TR strings and context for Dukan master marketing pages."""

from __future__ import annotations

import frappe

from saas_master.provisioning.urls import PUBLIC_IP

LANGS = ("en", "ar", "tr")

def _demo_img(photo_id: str) -> str:
	return (
		f"https://images.unsplash.com/photo-{photo_id}"
		f"?auto=format&fit=crop&w=800&h=520&q=80"
	)


DEMO_TEMPLATES = [
	{
		"key": "fashion",
		"name_en": "Noir Lane",
		"name_ar": "نوار لين",
		"name_tr": "Noir Lane",
		"niche_en": "Fashion",
		"niche_ar": "أزياء",
		"niche_tr": "Moda",
		"color": "#0A0A0A",
		"accent": "#D4FF00",
		"image": _demo_img("1483985988355-763728e1935b"),
	},
	{
		"key": "electronics",
		"name_en": "Volt Lab",
		"name_ar": "فولت لاب",
		"name_tr": "Volt Lab",
		"niche_en": "Electronics",
		"niche_ar": "إلكترونيات",
		"niche_tr": "Elektronik",
		"color": "#030712",
		"accent": "#22D3EE",
		"image": _demo_img("1518770660439-4636190af475"),
	},
	{
		"key": "beauty",
		"name_en": "Maison Glow",
		"name_ar": "ميزون غلو",
		"name_tr": "Maison Glow",
		"niche_en": "Beauty",
		"niche_ar": "تجميل",
		"niche_tr": "Güzellik",
		"color": "#4A1942",
		"accent": "#C9A227",
		"image": _demo_img("1596462502278-27bfdc403348"),
	},
	{
		"key": "home",
		"name_en": "Clay & Loom",
		"name_ar": "كلاي آند لوم",
		"name_tr": "Clay & Loom",
		"niche_en": "Home",
		"niche_ar": "منزل",
		"niche_tr": "Ev",
		"color": "#5C3310",
		"accent": "#E07A3D",
		"image": _demo_img("1616486338812-3dadae4b4ace"),
	},
]

# key -> {en, ar, tr}
T = {
	"announcement": {
		"en": "Free during beta · No credit card · Launch in minutes",
		"ar": "مجاني أثناء البيتا · بدون بطاقة · متجرك جاهز خلال دقائق",
		"tr": "Beta süresince ücretsiz · Kart yok · Dakikalar içinde açılış",
	},
	"nav_solutions": {"en": "Solutions", "ar": "الحلول", "tr": "Çözümler"},
	"nav_pricing": {"en": "Pricing", "ar": "الأسعار", "tr": "Fiyatlar"},
	"nav_templates": {"en": "Templates", "ar": "القوالب", "tr": "Şablonlar"},
	"nav_login": {"en": "Login", "ar": "تسجيل الدخول", "tr": "Giriş"},
	"cta_create": {"en": "Create your store", "ar": "أنشئ متجرك", "tr": "Mağazanı oluştur"},
	"cta_create_free": {
		"en": "Create your store — free",
		"ar": "أنشئ متجرك مجاناً",
		"tr": "Ücretsiz mağaza oluştur",
	},
	"cta_demos": {"en": "See live demos", "ar": "شاهد المتاجر التجريبية", "tr": "Canlı demoları gör"},
	"cta_get_started": {"en": "Get started", "ar": "ابدأ الآن", "tr": "Hemen başla"},
	"hero_title": {
		"en": "Your store. Real books. Live in minutes.",
		"ar": "متجرك. محاسبة حقيقية. جاهز خلال دقائق.",
		"tr": "Mağazan. Gerçek muhasebe. Dakikalar içinde yayında.",
	},
	"hero_sub": {
		"en": "Dukan launches a complete online store — catalog, inventory, orders, returns, and accounting — with niche templates ready to sell.",
		"ar": "دكّان يطلق متجراً إلكترونياً كاملاً — كتالوج، مخزون، طلبات، مرتجعات، ومحاسبة — مع قوالب جاهزة للبيع.",
		"tr": "Dukan tam bir online mağaza açar — katalog, stok, sipariş, iade ve muhasebe — satışa hazır niş şablonlarla.",
	},
	"proof_line": {
		"en": "Built for merchants who outgrow toy store builders",
		"ar": "للتجار الذين تجاوزوا أدوات المتاجر البسيطة",
		"tr": "Basit mağaza araçlarını aşan işletmeler için",
	},
	"proof_1": {"en": "4 niche templates", "ar": "4 قوالب متخصصة", "tr": "4 niş şablon"},
	"proof_2": {"en": "TR · EN · AR storefront", "ar": "واجهة عربية · إنجليزية · تركية", "tr": "TR · EN · AR vitrin"},
	"proof_3": {"en": "ERP-grade inventory", "ar": "مخزون بمستوى أنظمة ERP", "tr": "ERP seviyesinde stok"},
	"sec_solutions": {"en": "Everything that runs a store", "ar": "كل ما يُشغّل متجرك", "tr": "Mağazayı yöneten her şey"},
	"sec_solutions_sub": {
		"en": "Ship a modern storefront with a real back office — not a disconnected CMS.",
		"ar": "أطلق واجهة حديثة مع خلفية محاسبية حقيقية — لا نظام محتوى منفصل.",
		"tr": "Modern vitrin + gerçek arka ofis — kopuk bir CMS değil.",
	},
	"sol_storefront_t": {"en": "Storefront", "ar": "المتجر الإلكتروني", "tr": "Vitrin"},
	"sol_storefront_d": {
		"en": "Catalog, variants, wishlist, reviews, guest checkout.",
		"ar": "كتالوج، متغيرات، قائمة أمنيات، تقييمات، شراء كزائر.",
		"tr": "Katalog, varyant, istek listesi, yorum, misafir ödeme.",
	},
	"sol_inventory_t": {"en": "Inventory & ERP", "ar": "المخزون والمحاسبة", "tr": "Stok ve ERP"},
	"sol_inventory_d": {
		"en": "Warehouses, stock, delivery notes, invoices, VAT-ready books.",
		"ar": "مستودعات، مخزون، سندات تسليم، فواتير، ضريبة جاهزة.",
		"tr": "Depo, stok, irsaliye, fatura, KDV’ye hazır defterler.",
	},
	"sol_orders_t": {"en": "Orders & returns", "ar": "الطلبات والمرتجعات", "tr": "Sipariş ve iade"},
	"sol_orders_d": {
		"en": "Sales orders through structured return requests with stock checks.",
		"ar": "طلبات بيع ومرتجعات منظمة مع فحص المخزون.",
		"tr": "Satış siparişinden yapılandırılmış iadeye, stok kontrolüyle.",
	},
	"sol_lang_t": {"en": "Multi-language", "ar": "تعدد اللغات", "tr": "Çok dil"},
	"sol_lang_d": {
		"en": "Turkish, English, and Arabic with full RTL on the storefront.",
		"ar": "العربية والإنجليزية والتركية مع دعم كامل لـ RTL.",
		"tr": "Türkçe, İngilizce, Arapça — tam RTL vitrin.",
	},
	"sol_pay_t": {"en": "Payments", "ar": "المدفوعات", "tr": "Ödemeler"},
	"sol_pay_d": {
		"en": "COD and mock online today — live gateways on the roadmap.",
		"ar": "الدفع عند الاستلام وتجربة دفع الآن — بوابات حية قريباً.",
		"tr": "Kapıda ödeme ve demo online — canlı gateway’ler yolda.",
	},
	"sol_ship_t": {"en": "Shipping", "ar": "الشحن", "tr": "Kargo"},
	"sol_ship_d": {
		"en": "Flat rate and free-shipping thresholds — carriers coming next.",
		"ar": "سعر ثابت وحد للشحن المجاني — شركات الشحن قريباً.",
		"tr": "Sabit ücret ve ücretsiz kargo eşiği — kargo ağları sonra.",
	},
	"badge_available": {"en": "Available", "ar": "متاح", "tr": "Hazır"},
	"badge_coming": {"en": "Coming soon", "ar": "قريباً", "tr": "Yakında"},
	"sec_audience": {"en": "Wherever you are in the journey", "ar": "أينما كنت في رحلتك", "tr": "Yolculuğunun her aşamasında"},
	"aud_1_t": {"en": "Idea stage", "ar": "أصحاب الأفكار", "tr": "Fikir aşaması"},
	"aud_1_d": {
		"en": "Pick a niche template and go live without building from zero.",
		"ar": "اختر قالباً متخصصاً وانطلق دون البناء من الصفر.",
		"tr": "Niş şablon seç, sıfırdan kurmadan yayına al.",
	},
	"aud_2_t": {"en": "Physical shop", "ar": "أصحاب المحلات", "tr": "Fiziksel mağaza"},
	"aud_2_d": {
		"en": "Add an online channel with inventory that matches your shelves.",
		"ar": "أضف قناة أونلاين بمخزون يتوافق مع متجرك الفعلي.",
		"tr": "Raftaki stokla uyumlu online kanal ekle.",
	},
	"aud_3_t": {"en": "Online already", "ar": "متاجر إلكترونية قائمة", "tr": "Zaten online"},
	"aud_3_d": {
		"en": "Move to an ERP-backed stack for orders, stock, and invoicing.",
		"ar": "انتقل لمنصة بمحاسبة حقيقية للطلبات والمخزون والفوترة.",
		"tr": "Sipariş, stok ve fatura için ERP destekli yığına geç.",
	},
	"aud_4_t": {"en": "Growing brand", "ar": "علامات في نمو", "tr": "Büyüyen marka"},
	"aud_4_d": {
		"en": "Scale with roles, warehouses, and a proper back office.",
		"ar": "توسّع بصلاحيات ومستودعات وخلفية احترافية.",
		"tr": "Roller, depolar ve gerçek arka ofisle ölçeklen.",
	},
	"sec_templates": {"en": "Start from a niche that fits", "ar": "ابدأ من قالب يناسب تخصصك", "tr": "Sana uyan nişle başla"},
	"sec_templates_sub": {
		"en": "Open a live demo store — same engine every new merchant gets.",
		"ar": "افتح متجراً تجريبياً حياً — نفس المحرك لكل تاجر جديد.",
		"tr": "Canlı demo mağaza aç — her yeni tüccarın motoru aynı.",
	},
	"open_demo": {"en": "Open demo", "ar": "افتح التجربة", "tr": "Demoyu aç"},
	"sec_how": {"en": "How it works", "ar": "كيف يعمل", "tr": "Nasıl çalışır"},
	"how_1_t": {"en": "Tell us about the business", "ar": "أخبرنا عن نشاطك", "tr": "İşletmeni anlat"},
	"how_1_d": {
		"en": "Company, industry, country, and currency — we set up the books.",
		"ar": "الشركة، القطاع، الدولة، والعملة — نجهّز الدفاتر.",
		"tr": "Şirket, sektör, ülke, para birimi — defterleri kurarız.",
	},
	"how_2_t": {"en": "Pick a look", "ar": "اختر المظهر", "tr": "Görünümü seç"},
	"how_2_d": {
		"en": "Choose a Fashion, Electronics, Beauty, or Home template.",
		"ar": "اختر قالب أزياء أو إلكترونيات أو تجميل أو منزل.",
		"tr": "Moda, elektronik, güzellik veya ev şablonu seç.",
	},
	"how_3_t": {"en": "Claim your address", "ar": "احجز عنوانك", "tr": "Adresini al"},
	"how_3_d": {
		"en": "yourbrand.flexloopers.com — connect a custom domain later.",
		"ar": "yourbrand.flexloopers.com — اربط نطاقك لاحقاً.",
		"tr": "yourbrand.flexloopers.com — özel alan adını sonra bağla.",
	},
	"how_4_t": {"en": "Start selling", "ar": "ابدأ البيع", "tr": "Satışa başla"},
	"how_4_d": {
		"en": "We provision storefront + ERP back office automatically.",
		"ar": "نجهّز الواجهة والخلفية المحاسبية تلقائياً.",
		"tr": "Vitrin + ERP arka ofisi otomatik kurulur.",
	},
	"sec_diff": {
		"en": "Real ERP back office — not a toy store builder",
		"ar": "خلفية ERP حقيقية — ليست أداة متجر بسيطة",
		"tr": "Gerçek ERP arka ofis — oyuncak mağaza aracı değil",
	},
	"sec_diff_sub": {
		"en": "Competitors win on local payment and shipping networks. We win when you need stock, invoicing, and operations that scale.",
		"ar": "المنافسون يتفوقون بشبكات الدفع والشحن المحلية. نحن نتفوق عندما تحتاج مخزوناً وفوترة وتشغيلاً قابلاً للتوسع.",
		"tr": "Rakipler yerel ödeme/kargo ağında güçlü. Biz stok, fatura ve ölçeklenebilir operasyonda güçlüyüz.",
	},
	"banner_title": {"en": "Free during beta", "ar": "مجاني أثناء البيتا", "tr": "Beta’da ücretsiz"},
	"banner_sub": {
		"en": "Create your store today — no credit card, no commitment.",
		"ar": "أنشئ متجرك اليوم — بدون بطاقة وبدون التزام.",
		"tr": "Bugün mağazanı aç — kart yok, taahhüt yok.",
	},
	"footer_copy": {
		"en": "Dukan by ahmad18189",
		"ar": "دكّان من ahmad18189",
		"tr": "ahmad18189’dan Dukan",
	},
	"footer_contact": {"en": "Contact", "ar": "تواصل", "tr": "İletişim"},
	# solutions page
	"solutions_title": {"en": "Solutions", "ar": "الحلول", "tr": "Çözümler"},
	"solutions_lead": {
		"en": "What Dukan ships today — and what is on the roadmap versus platforms like Zid and Salla.",
		"ar": "ما يوفّره دكّان اليوم — وما هو على خارطة الطريق مقارنة بمنصات مثل زد وسلة.",
		"tr": "Dukan’ın bugün sunduğu — ve Zid / Salla’ya göre yol haritası.",
	},
	# pricing page
	"pricing_title": {"en": "Pricing", "ar": "الأسعار", "tr": "Fiyatlar"},
	"pricing_lead": {
		"en": "Simple while we are in beta. Paid tiers are planned — not billed yet.",
		"ar": "بسيط أثناء البيتا. الباقات المدفوعة مخططة — لا فوترة بعد.",
		"tr": "Beta’da sade. Ücretli paketler planlandı — henüz faturalandırılmıyor.",
	},
	"plan_beta": {"en": "Beta Free", "ar": "بيتا مجاني", "tr": "Beta Ücretsiz"},
	"plan_beta_price": {"en": "0", "ar": "0", "tr": "0"},
	"plan_beta_period": {"en": "/ month during beta", "ar": "/ شهر أثناء البيتا", "tr": "/ ay (beta)"},
	"plan_starter": {"en": "Starter", "ar": "الانطلاقة", "tr": "Başlangıç"},
	"plan_growth": {"en": "Growth", "ar": "النمو", "tr": "Büyüme"},
	"plan_pro": {"en": "Pro", "ar": "احترافي", "tr": "Pro"},
	"plan_planned": {"en": "Planned", "ar": "مخطط", "tr": "Planlandı"},
	"plan_current": {"en": "Current", "ar": "الحالي", "tr": "Güncel"},
	"feat_store": {"en": "Online store + niche template", "ar": "متجر + قالب متخصص", "tr": "Online mağaza + niş şablon"},
	"feat_erp": {"en": "Inventory, orders, invoices", "ar": "مخزون، طلبات، فواتير", "tr": "Stok, sipariş, fatura"},
	"feat_lang": {"en": "TR / EN / AR storefront", "ar": "واجهة ع / إ / ت", "tr": "TR / EN / AR vitrin"},
	"feat_cod": {"en": "COD + checkout", "ar": "الدفع عند الاستلام", "tr": "Kapıda ödeme"},
	"feat_pay": {"en": "Live payment gateways", "ar": "بوابات دفع حية", "tr": "Canlı ödeme"},
	"feat_ship": {"en": "Carrier shipping labels", "ar": "بوليصات شركات الشحن", "tr": "Kargo etiketleri"},
	"feat_domain": {"en": "Custom domain assist", "ar": "مساعدة النطاق الخاص", "tr": "Özel alan adı desteği"},
	"feat_pos": {"en": "POS / cashier", "ar": "نقاط البيع", "tr": "POS / kasa"},
	"feat_apps": {"en": "Apps marketplace", "ar": "سوق التطبيقات", "tr": "Uygulama pazarı"},
	"feat_support": {"en": "Priority support", "ar": "دعم أولوية", "tr": "Öncelikli destek"},
	"page_home_title": {
		"en": "Dukan — Launch your online store in minutes",
		"ar": "دكّان — أنشئ متجرك الإلكتروني خلال دقائق",
		"tr": "Dukan — Online mağazanı dakikalar içinde aç",
	},
}


def resolve_lang() -> str:
	lang = (frappe.form_dict.get("lang") or "").strip().lower()
	if lang in LANGS:
		return lang
	cookie = (frappe.request.cookies.get("sm_lang") or "").strip().lower() if frappe.request else ""
	if cookie in LANGS:
		return cookie
	# Accept-Language sniff
	al = (frappe.get_request_header("Accept-Language") or "").lower()
	for code in ("ar", "tr", "en"):
		if code in al:
			return code
	return "en"


def t(key: str, lang: str) -> str:
	row = T.get(key) or {}
	return row.get(lang) or row.get("en") or key


def apply_marketing_context(context, page: str = "home"):
	lang = resolve_lang()
	context.no_cache = 1
	context.full_width = 1
	context.sm_lang = lang
	context.sm_dir = "rtl" if lang == "ar" else "ltr"
	context.html_dir = context.sm_dir
	context.html_lang = lang
	context.sm = frappe._dict({k: t(k, lang) for k in T})
	context.sm_langs = [
		{"code": "ar", "label": "AR"},
		{"code": "en", "label": "EN"},
		{"code": "tr", "label": "TR"},
	]
	demos = []
	for d in DEMO_TEMPLATES:
		demos.append(
			frappe._dict(
				{
					"key": d["key"],
					"url": f"https://{d['key']}.flexloopers.com/",
					"name": d[f"name_{lang}"] if f"name_{lang}" in d else d["name_en"],
					"niche": d[f"niche_{lang}"] if f"niche_{lang}" in d else d["niche_en"],
					"color": d["color"],
					"accent": d["accent"],
					"image": d.get("image") or "",
				}
			)
		)
	context.sm_demos = demos
	context.sm_public_ip = PUBLIC_IP
	context.sm_page = page
	user = frappe.session.user
	context.sm_show_landing_editor = bool(
		user
		and user != "Guest"
		and (user == "Administrator" or "System Manager" in frappe.get_roles(user))
	)
	if page == "home":
		context.title = t("page_home_title", lang)
	elif page == "solutions":
		context.title = t("solutions_title", lang) + " — Dukan"
	elif page == "pricing":
		context.title = t("pricing_title", lang) + " — Dukan"
	return context
