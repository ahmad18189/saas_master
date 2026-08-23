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
		"desc_en": "Ink + neon streetwear. Mall-priced apparel ready to sell.",
		"desc_ar": "أزياء شارع بحبر ونيون — ملابس بأسعار المول جاهزة للبيع.",
		"desc_tr": "Mürekkep + neon streetwear. AVM fiyatlı giyim, satışa hazır.",
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
		"desc_en": "Dark neon tech — earbuds, GaN chargers, and docks.",
		"desc_ar": "تقنية نيون داكنة — سماعات وشواحن ومنصات توصيل.",
		"desc_tr": "Koyu neon teknoloji — kulaklık, GaN şarj ve dock’lar.",
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
		"desc_en": "Plum & gold rituals — boutique skincare and scent.",
		"desc_ar": "طقوس برقوقي وذهبي — عناية بالبشرة وعطور بوتيك.",
		"desc_tr": "Mürdüm & altın ritüeller — butik cilt bakımı ve koku.",
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
		"desc_en": "Terracotta living — ceramics, kitchen, and textiles.",
		"desc_ar": "أجواء تيراكوتا — سيراميك ومطبخ ومنسوجات.",
		"desc_tr": "Terrakota yaşam — seramik, mutfak ve tekstil.",
		"color": "#5C3310",
		"accent": "#E07A3D",
		"image": _demo_img("1616486338812-3dadae4b4ace"),
	},
]


def _pillar_img(photo_id: str) -> str:
	return (
		f"https://images.unsplash.com/photo-{photo_id}"
		f"?auto=format&fit=crop&w=900&h=560&q=80"
	)


# Feature-pillar photos (storefront, inventory, orders, languages, payments, shipping)
PILLAR_IMAGES = [
	_pillar_img("1534452203293-494d7ddbf7e0"),
	_pillar_img("1553413077-190dd305871c"),
	_pillar_img("1566576912321-d58ddd7a6088"),
	_pillar_img("1523240795612-9a054b0db644"),
	_pillar_img("1556742049-0cfed4f6a45d"),
	_pillar_img("1519003722824-194d4455a60c"),
]

# Audience photos (idea stage, physical shop, already online, growing brand)
AUDIENCE_IMAGES = [
	_pillar_img("1517245386807-bb43f82c33c4"),
	_pillar_img("1604719312566-8912e9227c6a"),
	_pillar_img("1460925895917-afdab827c52f"),
	_pillar_img("1522071820081-009f0129c71c"),
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
		"en": "What Dukan ships today — and what is on the product roadmap.",
		"ar": "ما يوفّره دكّان اليوم — وما هو على خارطة طريق المنتج.",
		"tr": "Dukan’ın bugün sunduğu — ve ürün yol haritası.",
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
	# ----- signup wizard -----
	"su_title": {"en": "Create your store — Dukan", "ar": "أنشئ متجرك — دكّان", "tr": "Mağazanı oluştur — Dukan"},
	"su_hero_kicker": {"en": "Launch in minutes", "ar": "انطلق خلال دقائق", "tr": "Dakikalar içinde aç"},
	"su_hero_title": {
		"en": "Build a real store with ERP back office",
		"ar": "أنشئ متجراً حقيقياً بخلفية محاسبية",
		"tr": "ERP arka ofisli gerçek bir mağaza kur",
	},
	"su_hero_sub": {
		"en": "Built for KSA merchants — inventory, invoices, and a multilingual storefront in one stack.",
		"ar": "مصمم لتجار السعودية — مخزون وفواتير وواجهة متعددة اللغات في منصة واحدة.",
		"tr": "KSA işletmeleri için — stok, fatura ve çok dilli vitrin tek stack’te.",
	},
	"su_back": {"en": "Back", "ar": "رجوع", "tr": "Geri"},
	"su_next": {"en": "Next", "ar": "التالي", "tr": "İleri"},
	"su_create": {"en": "Create my store", "ar": "أنشئ متجري", "tr": "Mağazamı oluştur"},
	"su_creating": {"en": "Creating…", "ar": "جارٍ الإنشاء…", "tr": "Oluşturuluyor…"},
	"su_step_company": {"en": "Company", "ar": "الشركة", "tr": "Şirket"},
	"su_step_plan": {"en": "Plan", "ar": "الباقة", "tr": "Plan"},
	"su_step_look": {"en": "Look", "ar": "المظهر", "tr": "Görünüm"},
	"su_step_you": {"en": "You", "ar": "أنت", "tr": "Sen"},
	"su_step_address": {"en": "Address", "ar": "العنوان", "tr": "Adres"},
	"su_step_review": {"en": "Review", "ar": "مراجعة", "tr": "Özet"},
	"su_h_company": {"en": "Tell us about your business", "ar": "أخبرنا عن عملك", "tr": "İşletmeni anlat"},
	"su_company_name": {"en": "Company name *", "ar": "اسم الشركة *", "tr": "Şirket adı *"},
	"su_company_name_ph": {"en": "e.g. Nordic Clothing Co.", "ar": "مثال: متجر الأناقة", "tr": "örn. Nordic Giyim"},
	"su_company_city": {"en": "City", "ar": "المدينة", "tr": "Şehir"},
	"su_company_city_ph": {"en": "Riyadh, Istanbul, Dubai…", "ar": "الرياض، إسطنبول، دبي…", "tr": "Riyad, İstanbul, Dubai…"},
	"su_company_desc": {"en": "What do you sell?", "ar": "ماذا تبيع؟", "tr": "Ne satıyorsun?"},
	"su_company_desc_ph": {
		"en": "Short description of your products or services",
		"ar": "وصف مختصر لمنتجاتك أو خدماتك",
		"tr": "Ürün / hizmetlerin kısa açıklaması",
	},
	"su_industry": {"en": "Industry *", "ar": "القطاع *", "tr": "Sektör *"},
	"su_industry_hint": {
		"en": "Helps us match a starter template on the next steps.",
		"ar": "يساعدنا على اقتراح قالب مناسب في الخطوات التالية.",
		"tr": "Sonraki adımlarda şablon önermemize yardımcı olur.",
	},
	"su_ind_clothing": {"en": "Clothing", "ar": "ملابس", "tr": "Giyim"},
	"su_ind_electronics": {"en": "Electronics", "ar": "إلكترونيات", "tr": "Elektronik"},
	"su_ind_beauty": {"en": "Beauty", "ar": "تجميل", "tr": "Güzellik"},
	"su_ind_home": {"en": "Home", "ar": "منزل", "tr": "Ev"},
	"su_ind_grocery": {"en": "Grocery", "ar": "بقالة", "tr": "Market"},
	"su_ind_services": {"en": "Services", "ar": "خدمات", "tr": "Hizmetler"},
	"su_ind_other": {"en": "Other", "ar": "أخرى", "tr": "Diğer"},
	"su_country": {"en": "Country *", "ar": "الدولة *", "tr": "Ülke *"},
	"su_currency": {"en": "Currency *", "ar": "العملة *", "tr": "Para birimi *"},
	"su_h_plan": {
		"en": "How big is your catalog?",
		"ar": "ما حجم كتالوجك؟",
		"tr": "Kataloğun ne kadar büyük?",
	},
	"su_plan_lead": {
		"en": "We’ll suggest Free, Growth, or Enterprise based on your catalog size. Beta is free to use.",
		"ar": "نقترح مجاني أو نمو أو مؤسسات حسب حجم كتالوجك. البيتا مجانية للاستخدام.",
		"tr": "Katalog boyutuna göre Ücretsiz, Büyüme veya Kurumsal öneririz. Beta ücretsiz.",
	},
	"su_products": {"en": "Expected products / SKUs *", "ar": "عدد المنتجات المتوقع *", "tr": "Beklenen ürün / SKU *"},
	"su_band_50": {"en": "Up to 50", "ar": "حتى 50", "tr": "50’ye kadar"},
	"su_band_200": {"en": "51 – 200", "ar": "51 – 200", "tr": "51 – 200"},
	"su_band_1000": {"en": "201 – 1,000", "ar": "201 – 1,000", "tr": "201 – 1.000"},
	"su_band_plus": {"en": "1,000+", "ar": "أكثر من 1,000", "tr": "1.000+"},
	"su_support": {"en": "Support level you need", "ar": "مستوى الدعم المطلوب", "tr": "İhtiyacın olan destek"},
	"su_support_community": {"en": "Community / email", "ar": "مجتمع / بريد", "tr": "Topluluk / e-posta"},
	"su_support_chat": {"en": "Priority chat", "ar": "دردشة بأولوية", "tr": "Öncelikli sohbet"},
	"su_support_dedicated": {"en": "Dedicated manager", "ar": "مدير حساب مخصص", "tr": "Özel hesap yöneticisi"},
	"su_suggested": {"en": "Suggested for you", "ar": "مقترح لك", "tr": "Senin için önerilen"},
	"su_plan_free": {"en": "Free", "ar": "مجاني", "tr": "Ücretsiz"},
	"su_plan_free_price": {"en": "0 SAR / mo", "ar": "0 ر.س / شهر", "tr": "0 SAR / ay"},
	"su_plan_free_desc": {
		"en": "Up to ~100 products · Subdomain · Email support · Full ERP core",
		"ar": "حتى ~100 منتج · نطاق فرعي · دعم بريد · نواة ERP كاملة",
		"tr": "~100 ürüne kadar · Alt alan · E-posta destek · Tam ERP çekirdek",
	},
	"su_plan_growth": {"en": "Growth", "ar": "النمو", "tr": "Büyüme"},
	"su_plan_growth_price": {"en": "from 99 SAR / mo", "ar": "من 99 ر.س / شهر", "tr": "99 SAR / ay’dan"},
	"su_plan_growth_desc": {
		"en": "Unlimited products · Custom domain · Priority chat",
		"ar": "منتجات غير محدودة · نطاق خاص · دردشة بأولوية",
		"tr": "Sınırsız ürün · Özel alan · Öncelikli sohbet",
	},
	"su_plan_ent": {"en": "Enterprise", "ar": "مؤسسات", "tr": "Kurumsal"},
	"su_plan_ent_price": {"en": "Custom", "ar": "حسب الاتفاق", "tr": "Özel"},
	"su_plan_ent_desc": {
		"en": "Dedicated support · Multi-warehouse · SLA",
		"ar": "دعم مخصص · مستودعات متعددة · اتفاقية مستوى خدمة",
		"tr": "Özel destek · Çoklu depo · SLA",
	},
	"su_plan_beta_note": {
		"en": "All plans are free during beta — pick the tier that matches your scale.",
		"ar": "كل الباقات مجانية أثناء البيتا — اختر ما يناسب حجمك.",
		"tr": "Beta’da tüm planlar ücretsiz — ölçeğine uygun olanı seç.",
	},
	"su_h_look": {"en": "Choose your store look", "ar": "اختر مظهر متجرك", "tr": "Mağaza görünümünü seç"},
	"su_look_hint": {
		"en": "Pick a starter theme and demo catalog. You can change colors and products later.",
		"ar": "اختر قالباً وكتالوجاً تجريبياً. يمكنك تغيير الألوان والمنتجات لاحقاً.",
		"tr": "Başlangıç teması ve demo katalog seç. Renkleri ve ürünleri sonra değiştirebilirsin.",
	},
	"su_loading_templates": {"en": "Loading templates…", "ar": "جارٍ تحميل القوالب…", "tr": "Şablonlar yükleniyor…"},
	"su_h_you": {"en": "Your info", "ar": "معلوماتك", "tr": "Bilgilerin"},
	"su_full_name": {"en": "Full name *", "ar": "الاسم الكامل *", "tr": "Ad soyad *"},
	"su_email": {"en": "Email *", "ar": "البريد الإلكتروني *", "tr": "E-posta *"},
	"su_email_hint": {"en": "This becomes your store login.", "ar": "سيصبح تسجيل دخول متجرك.", "tr": "Mağaza girişin olacak."},
	"su_phone": {"en": "Phone", "ar": "الجوال", "tr": "Telefon"},
	"su_phone_hint": {
		"en": "Search by country or calling code.",
		"ar": "ابحث بالدولة أو رمز الاتصال.",
		"tr": "Ülke veya alan koduyla ara.",
	},
	"su_password": {"en": "Password *", "ar": "كلمة المرور *", "tr": "Şifre *"},
	"su_password_hint": {"en": "At least 8 characters.", "ar": "8 أحرف على الأقل.", "tr": "En az 8 karakter."},
	"su_heard": {"en": "Where did you hear about us? *", "ar": "كيف سمعت عنا؟ *", "tr": "Bizi nereden duydun? *"},
	"su_heard_google": {"en": "Google / Search", "ar": "جوجل / بحث", "tr": "Google / Arama"},
	"su_heard_social": {"en": "Instagram / TikTok / Social", "ar": "إنستغرام / تيك توك / سوشيال", "tr": "Instagram / TikTok / Sosyal"},
	"su_heard_friend": {"en": "Friend / Colleague", "ar": "صديق / زميل", "tr": "Arkadaş / Meslektaş"},
	"su_heard_compare": {"en": "Comparing other platforms", "ar": "مقارنة مع منصات أخرى", "tr": "Diğer platformlarla karşılaştırma"},
	"su_heard_youtube": {"en": "YouTube / Content", "ar": "يوتيوب / محتوى", "tr": "YouTube / İçerik"},
	"su_heard_event": {"en": "Event / Conference", "ar": "فعالية / مؤتمر", "tr": "Etkinlik / Konferans"},
	"su_heard_other": {"en": "Other", "ar": "أخرى", "tr": "Diğer"},
	"su_h_address": {"en": "Your store address", "ar": "عنوان متجرك", "tr": "Mağaza adresin"},
	"su_website": {"en": "Current website (optional)", "ar": "موقعك الحالي (اختياري)", "tr": "Mevcut site (opsiyonel)"},
	"su_website_hint": {
		"en": "If you already have a domain, we can connect it later.",
		"ar": "إن كان لديك نطاق، يمكننا ربطه لاحقاً.",
		"tr": "Alan adın varsa sonra bağlarız.",
	},
	"su_subdomain": {"en": "Choose your store address *", "ar": "اختر عنوان متجرك *", "tr": "Mağaza adresini seç *"},
	"su_checking": {"en": "Checking…", "ar": "جارٍ التحقق…", "tr": "Kontrol…"},
	"su_available": {"en": "is available", "ar": "متاح", "tr": "müsait"},
	"su_h_review": {"en": "Review & create", "ar": "مراجعة وإنشاء", "tr": "Gözden geçir ve oluştur"},
	"su_agree": {
		"en": "By creating a store you agree to fair-use of the beta service.",
		"ar": "بإنشاء متجر فإنك توافق على الاستخدام العادل لخدمة البيتا.",
		"tr": "Mağaza oluşturarak beta hizmetinin adil kullanımını kabul edersin.",
	},
	"su_err_company": {"en": "Please enter your company name.", "ar": "أدخل اسم الشركة.", "tr": "Şirket adını gir."},
	"su_err_products": {"en": "Select how many products you expect.", "ar": "حدد عدد المنتجات المتوقع.", "tr": "Beklenen ürün sayısını seç."},
	"su_err_plan": {"en": "Please choose a plan.", "ar": "اختر باقة.", "tr": "Bir plan seç."},
	"su_err_template": {"en": "Please choose a store look.", "ar": "اختر مظهر المتجر.", "tr": "Bir görünüm seç."},
	"su_err_no_templates": {"en": "No store templates are available yet.", "ar": "لا توجد قوالب بعد.", "tr": "Henüz şablon yok."},
	"su_err_name": {"en": "Please enter your full name.", "ar": "أدخل اسمك الكامل.", "tr": "Adını gir."},
	"su_err_email": {"en": "Please enter a valid email.", "ar": "أدخل بريداً صالحاً.", "tr": "Geçerli e-posta gir."},
	"su_err_phone": {"en": "Please enter a valid phone number.", "ar": "أدخل رقم جوال صالحاً.", "tr": "Geçerli telefon gir."},
	"su_err_password": {"en": "Password must be at least 8 characters.", "ar": "كلمة المرور 8 أحرف على الأقل.", "tr": "Şifre en az 8 karakter olmalı."},
	"su_err_heard": {"en": "Tell us where you heard about us.", "ar": "أخبرنا كيف سمعت عنا.", "tr": "Bizi nereden duyduğunu seç."},
	"su_err_subdomain": {"en": "Please choose an available store address.", "ar": "اختر عنواناً متاحاً.", "tr": "Müsait bir adres seç."},
	"su_err_sub_invalid": {
		"en": "Address must be 3–31 characters: lowercase letters, digits and dashes, starting with a letter or digit.",
		"ar": "العنوان من 3 إلى 31 حرفاً: أحرف إنجليزية صغيرة وأرقام وشرطات، ويبدأ بحرف أو رقم.",
		"tr": "Adres 3–31 karakter olmalı: küçük harf, rakam ve tire; harf veya rakamla başlamalı.",
	},
	"su_err_sub_reserved": {
		"en": "This address is reserved.",
		"ar": "هذا العنوان محجوز.",
		"tr": "Bu adres ayrılmış.",
	},
	"su_err_sub_taken": {
		"en": "This address is already taken.",
		"ar": "هذا العنوان مستخدم بالفعل.",
		"tr": "Bu adres zaten alınmış.",
	},
	"su_err_sub_unavailable": {
		"en": "Not available.",
		"ar": "غير متاح.",
		"tr": "Müsait değil.",
	},
	"su_rev_company": {"en": "Company", "ar": "الشركة", "tr": "Şirket"},
	"su_rev_city": {"en": "City", "ar": "المدينة", "tr": "Şehir"},
	"su_rev_plan": {"en": "Plan", "ar": "الباقة", "tr": "Plan"},
	"su_rev_products": {"en": "Catalog size", "ar": "حجم الكتالوج", "tr": "Katalog boyutu"},
	"su_rev_look": {"en": "Store look", "ar": "مظهر المتجر", "tr": "Görünüm"},
	"su_rev_industry": {"en": "Industry", "ar": "القطاع", "tr": "Sektör"},
	"su_rev_country": {"en": "Country", "ar": "الدولة", "tr": "Ülke"},
	"su_rev_currency": {"en": "Currency", "ar": "العملة", "tr": "Para birimi"},
	"su_rev_owner": {"en": "Owner", "ar": "المالك", "tr": "Sahip"},
	"su_rev_email": {"en": "Email", "ar": "البريد", "tr": "E-posta"},
	"su_rev_phone": {"en": "Phone", "ar": "الجوال", "tr": "Telefon"},
	"su_rev_heard": {"en": "Heard about us", "ar": "مصدر المعرفة", "tr": "Nereden duydu"},
	"su_rev_website": {"en": "Current website", "ar": "الموقع الحالي", "tr": "Mevcut site"},
	"su_rev_address": {"en": "Store address", "ar": "عنوان المتجر", "tr": "Mağaza adresi"},
	# Signup status / provisioning page
	"st_title": {"en": "Creating your store — Dukan", "ar": "جارٍ إنشاء متجرك — دكّان", "tr": "Mağazan oluşturuluyor — Dukan"},
	"st_creating": {"en": "Creating your store…", "ar": "جارٍ إنشاء متجرك…", "tr": "Mağazan oluşturuluyor…"},
	"st_queue": {"en": "Waiting in queue…", "ar": "في قائمة الانتظار…", "tr": "Kuyrukta bekleniyor…"},
	"st_ready": {"en": "Your store is ready!", "ar": "متجرك جاهز!", "tr": "Mağazan hazır!"},
	"st_ready_sub": {
		"en": "HTTPS is verified — open your store securely.",
		"ar": "تم التحقق من HTTPS — افتح متجرك بأمان.",
		"tr": "HTTPS doğrulandı — mağazanı güvenle aç.",
	},
	"st_failed": {"en": "Something went wrong", "ar": "حدث خطأ ما", "tr": "Bir sorun oluştu"},
	"st_failed_sub": {
		"en": "Our team has been notified and will fix your store shortly.",
		"ar": "تم إشعار فريقنا وسيتم إصلاح متجرك قريباً.",
		"tr": "Ekibimiz bilgilendirildi; mağazan kısa sürede düzeltilir.",
	},
	"st_expired": {"en": "Link expired or invalid", "ar": "الرابط منتهٍ أو غير صالح", "tr": "Bağlantı geçersiz veya süresi dolmuş"},
	"st_try_again": {"en": "Try again", "ar": "حاول مجدداً", "tr": "Tekrar dene"},
	"st_back_signup": {"en": "Back to signup", "ar": "العودة للتسجيل", "tr": "Kayıta dön"},
	"st_open_store": {"en": "Open my store", "ar": "افتح متجري", "tr": "Mağazamı aç"},
	"st_store_address": {"en": "Store address", "ar": "عنوان المتجر", "tr": "Mağaza adresi"},
	"st_domain": {"en": "Domain", "ar": "النطاق", "tr": "Alan adı"},
	"st_login": {"en": "Login", "ar": "تسجيل الدخول", "tr": "Giriş"},
	"st_password": {"en": "Password", "ar": "كلمة المرور", "tr": "Şifre"},
	"st_password_once": {
		"en": "Save it now — shown only once.",
		"ar": "احفظها الآن — تُعرض مرة واحدة فقط.",
		"tr": "Şimdi kaydet — yalnızca bir kez gösterilir.",
	},
	"st_progress": {"en": "Provisioning progress", "ar": "تقدّم التجهيز", "tr": "Kurulum ilerlemesi"},
	"st_step1": {"en": "Create site", "ar": "إنشاء الموقع", "tr": "Site oluştur"},
	"st_step2": {"en": "Install store template", "ar": "تثبيت قالب المتجر", "tr": "Mağaza şablonunu kur"},
	"st_step3": {"en": "Configure company & books", "ar": "إعداد الشركة والمحاسبة", "tr": "Şirket ve defterleri ayarla"},
	"st_step4": {"en": "Create owner login", "ar": "إنشاء حساب المالك", "tr": "Sahip girişi oluştur"},
	"st_step5": {"en": "Apply store defaults", "ar": "تطبيق إعدادات المتجر", "tr": "Mağaza varsayılanlarını uygula"},
	"st_step6": {"en": "Secure HTTPS", "ar": "تأمين HTTPS", "tr": "HTTPS güvenceye al"},
	"st_label_create": {"en": "Creating your store…", "ar": "جارٍ إنشاء متجرك…", "tr": "Mağaza oluşturuluyor…"},
	"st_label_template": {"en": "Installing store template…", "ar": "جارٍ تثبيت قالب المتجر…", "tr": "Şablon kuruluyor…"},
	"st_label_account": {"en": "Setting up your account…", "ar": "جارٍ إعداد حسابك…", "tr": "Hesabın ayarlanıyor…"},
	"st_label_https": {"en": "Securing HTTPS… almost done", "ar": "تأمين HTTPS… أوشكنا على الانتهاء", "tr": "HTTPS güvenceye alınıyor… neredeyse bitti"},
	"st_hero_kicker": {"en": "While we build", "ar": "أثناء التجهيز", "tr": "Kurulum sürerken"},
	"st_slide1_t": {"en": "A real storefront, not a toy", "ar": "متجر حقيقي لا أداة بسيطة", "tr": "Gerçek vitrin — oyuncak değil"},
	"st_slide1_d": {
		"en": "Catalog, cart, checkout, and niche templates ready to sell.",
		"ar": "كتالوج وسلة ودفع وقوالب متخصصة جاهزة للبيع.",
		"tr": "Katalog, sepet, ödeme ve satışa hazır niş şablonlar.",
	},
	"st_slide2_t": {"en": "Inventory & ERP back office", "ar": "مخزون ومحاسبة خلفية", "tr": "Stok ve ERP arka ofis"},
	"st_slide2_d": {
		"en": "Warehouses, stock moves, delivery notes, and VAT-ready invoices.",
		"ar": "مستودعات وحركات مخزون وسندات تسليم وفواتير جاهزة للضريبة.",
		"tr": "Depo, stok hareketi, irsaliye ve KDV’ye hazır faturalar.",
	},
	"st_slide3_t": {"en": "Orders through returns", "ar": "من الطلب إلى المرتجع", "tr": "Siparişten iadeye"},
	"st_slide3_d": {
		"en": "Sales orders with structured returns and stock checks.",
		"ar": "طلبات بيع ومرتجعات منظمة مع فحص المخزون.",
		"tr": "Stok kontrollü satış siparişi ve yapılandırılmış iade.",
	},
	"st_slide4_t": {"en": "TR · EN · AR storefront", "ar": "واجهة ع · إ · ت", "tr": "TR · EN · AR vitrin"},
	"st_slide4_d": {
		"en": "Full multilingual storefront with RTL for Arabic.",
		"ar": "واجهة متعددة اللغات مع دعم كامل لـ RTL بالعربية.",
		"tr": "Arapça RTL dahil tam çok dilli vitrin.",
	},
	# —— Master login ——
	"lg_title": {"en": "Login — Dukan", "ar": "تسجيل الدخول — دكّان", "tr": "Giriş — Dukan"},
	"lg_aside_kicker": {"en": "Welcome back", "ar": "أهلاً بعودتك", "tr": "Tekrar hoş geldiniz"},
	"lg_aside_title": {
		"en": "Open your store desk",
		"ar": "افتح لوحة متجرك",
		"tr": "Mağaza paneline gir",
	},
	"lg_aside_sub": {
		"en": "Merchants sign in on their own store. Enter your address to continue.",
		"ar": "التجار يسجّلون الدخول على متجرهم. أدخل عنوانك للمتابعة.",
		"tr": "Satıcılar kendi mağazalarında giriş yapar. Devam için adresini gir.",
	},
	"lg_aside_b1": {
		"en": "Your store lives at brand.flexloopers.com",
		"ar": "متجرك على brand.flexloopers.com",
		"tr": "Mağazan brand.flexloopers.com adresinde",
	},
	"lg_aside_b2": {
		"en": "Owner email & password from signup",
		"ar": "بريد وكلمة مرور المالك من التسجيل",
		"tr": "Kayıttaki sahip e-postası ve şifresi",
	},
	"lg_aside_b3": {
		"en": "AR · EN · TR storefront ready",
		"ar": "واجهة ع · إ · ت جاهزة",
		"tr": "AR · EN · TR vitrin hazır",
	},
	"lg_store_heading": {"en": "Open your store", "ar": "افتح متجرك", "tr": "Mağazanı aç"},
	"lg_store_lead": {
		"en": "Enter the store address you chose at signup. We’ll take you to its login page.",
		"ar": "أدخل عنوان المتجر الذي اخترته عند التسجيل. سننقلك إلى صفحة الدخول.",
		"tr": "Kayıtta seçtiğin mağaza adresini gir. Seni giriş sayfasına götürelim.",
	},
	"lg_store_address": {"en": "Store address", "ar": "عنوان المتجر", "tr": "Mağaza adresi"},
	"lg_store_ph": {"en": "yourbrand", "ar": "علامتك", "tr": "markan"},
	"lg_email_lookup": {
		"en": "Or look up by signup email",
		"ar": "أو ابحث ببريد التسجيل",
		"tr": "Veya kayıt e-postasıyla bul",
	},
	"lg_email_ph": {"en": "you@example.com", "ar": "you@example.com", "tr": "you@example.com"},
	"lg_email_hint": {
		"en": "Optional if you already know your store address.",
		"ar": "اختياري إن كنت تعرف عنوان متجرك.",
		"tr": "Mağaza adresini biliyorsan isteğe bağlı.",
	},
	"lg_continue": {"en": "Continue to store", "ar": "المتابعة إلى المتجر", "tr": "Mağazaya devam"},
	"lg_checking": {"en": "Checking…", "ar": "جارٍ التحقق…", "tr": "Kontrol…"},
	"lg_no_store": {"en": "Don’t have a store yet?", "ar": "ليس لديك متجر بعد؟", "tr": "Henüz mağazan yok mu?"},
	"lg_create_store": {"en": "Create your store", "ar": "أنشئ متجرك", "tr": "Mağazanı oluştur"},
	"lg_platform_link": {
		"en": "Platform team? Sign in",
		"ar": "فريق المنصة؟ سجّل الدخول",
		"tr": "Platform ekibi? Giriş yap",
	},
	"lg_ops_heading": {"en": "Platform sign in", "ar": "دخول المنصة", "tr": "Platform girişi"},
	"lg_ops_lead": {
		"en": "For Dukan operators and landing editors only.",
		"ar": "لمشغّلي دكّان ومحرري الصفحة فقط.",
		"tr": "Yalnızca Dukan operatörleri ve landing editörleri için.",
	},
	"lg_back_store": {"en": "← Back to open your store", "ar": "→ العودة لفتح متجرك", "tr": "← Mağazanı açmaya dön"},
	"lg_pick_store": {"en": "Choose a store:", "ar": "اختر متجراً:", "tr": "Bir mağaza seç:"},
	"lg_err_empty": {
		"en": "Enter your store address or the email you signed up with.",
		"ar": "أدخل عنوان متجرك أو بريد التسجيل.",
		"tr": "Mağaza adresini veya kayıt e-postanı gir.",
	},
	"lg_err_not_found": {
		"en": "We couldn’t find that store. Check the address or create a new one.",
		"ar": "لم نعثر على ذلك المتجر. تحقق من العنوان أو أنشئ متجراً جديداً.",
		"tr": "Mağaza bulunamadı. Adresi kontrol et veya yeni oluştur.",
	},
	"lg_err_provisioning": {
		"en": "Your store is still being built. Try again in a few minutes.",
		"ar": "متجرك ما زال قيد التجهيز. حاول بعد دقائق.",
		"tr": "Mağazan hâlâ kuruluyor. Birkaç dakika sonra tekrar dene.",
	},
	"lg_err_unavailable": {
		"en": "This store is not available right now.",
		"ar": "هذا المتجر غير متاح حالياً.",
		"tr": "Bu mağaza şu an kullanılamıyor.",
	},
	"lg_err_multiple": {
		"en": "We found more than one store for that email. Pick one below.",
		"ar": "وجدنا أكثر من متجر لهذا البريد. اختر واحداً أدناه.",
		"tr": "Bu e-posta için birden fazla mağaza var. Aşağıdan birini seç.",
	},
	"lg_err_generic": {
		"en": "Something went wrong. Please try again.",
		"ar": "حدث خطأ. حاول مرة أخرى.",
		"tr": "Bir şeyler ters gitti. Lütfen tekrar dene.",
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
	context.sm_pillar_images = PILLAR_IMAGES
	context.sm_audience_images = AUDIENCE_IMAGES
	context.favicon = "/assets/saas_master/images/dukan-favicon.svg"
	# Landing editor is desk-only — never surface a public-site edit link
	context.sm_show_landing_editor = False
	# Apply saved light/dark mode before first paint (head.html emits head_html first)
	boot = (
		'<script id="sm-mode-boot">(function(){try{var m=document.cookie.match(/(?:^|; )sm_mode=([^;]*)/);'
		'var v=m?decodeURIComponent(m[1]):"";if(v!=="dark"&&v!=="light"){'
		'v=(window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches)?"dark":"light";}'
		'document.documentElement.setAttribute("data-sm-mode",v);'
		'document.documentElement.style.colorScheme=v;}catch(e){}})();</script>'
	)
	context.head_html = boot + (context.get("head_html") or "")
	if page == "home":
		context.title = t("page_home_title", lang)
	elif page == "solutions":
		context.title = t("solutions_title", lang) + " — Dukan"
	elif page == "pricing":
		context.title = t("pricing_title", lang) + " — Dukan"
	elif page == "signup":
		context.title = t("su_title", lang)
	elif page == "login":
		context.title = t("lg_title", lang)
	try:
		from saas_master.api.marketing_editor import overlay_chrome_on_context

		overlay_chrome_on_context(context)
	except Exception:
		context.sm_brand_html = context.get("sm_brand_html") or "Du<span>kan</span>"
		sm = context.get("sm")
		if sm is not None:
			sm.brand_mark = sm.get("brand_mark") or "Dukan"
			sm.home_href = sm.get("home_href") or ("/?lang=" + lang)
			sm.nav_solutions_href = sm.get("nav_solutions_href") or ("/solutions?lang=" + lang)
			sm.nav_pricing_href = sm.get("nav_pricing_href") or ("/pricing?lang=" + lang)
			sm.nav_templates_href = sm.get("nav_templates_href") or "#templates"
			sm.nav_login_href = sm.get("nav_login_href") or ("/login?lang=" + lang)
			sm.cta_create_href = sm.get("cta_create_href") or ("/signup?lang=" + lang)
			sm.contact_email = sm.get("contact_email") or "dev@flexloopers.com"
			sm.contact_url = sm.get("contact_url") or "https://flexloopers.com"
			sm.contact_url_label = sm.get("contact_url_label") or "flexloopers.com"
			sm.footer_legal = sm.get("footer_legal") or sm.get("footer_copy") or ""
			sm.copyright_year = sm.get("copyright_year") or "2026"
	return context
