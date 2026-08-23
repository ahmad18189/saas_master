"""Seed default Signup Aside Step rows (idempotent)."""

from __future__ import annotations

import frappe

DEFAULTS = [
	{
		"step": 1,
		"step_key": "company",
		"image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1200&h=1600&q=80",
		"kicker_en": "Step 1 · Company",
		"kicker_ar": "الخطوة 1 · الشركة",
		"kicker_tr": "Adım 1 · Şirket",
		"title_en": "Tell us about your business",
		"title_ar": "أخبرنا عن عملك",
		"title_tr": "İşletmeni anlat",
		"subtitle_en": "Industry, city, and country help us match the right store template and books.",
		"subtitle_ar": "القطاع والمدينة والدولة تساعدنا على اختيار القالب والمحاسبة المناسبة.",
		"subtitle_tr": "Sektör, şehir ve ülke doğru şablon ve muhasebe kurulumunu seçmemize yardım eder.",
		"bullet_1_icon": "🏢",
		"bullet_1_en": "Company profile for invoices & legal name",
		"bullet_1_ar": "ملف الشركة للفواتير والاسم القانوني",
		"bullet_1_tr": "Fatura ve yasal ad için şirket profili",
		"bullet_2_icon": "🌍",
		"bullet_2_en": "Country & currency for tax-ready books",
		"bullet_2_ar": "الدولة والعملة لمحاسبة جاهزة للضريبة",
		"bullet_2_tr": "Vergiye hazır defterler için ülke ve para birimi",
		"bullet_3_icon": "🧭",
		"bullet_3_en": "Industry steers your starter catalog",
		"bullet_3_ar": "القطاع يوجّه كتالوج البداية",
		"bullet_3_tr": "Sektör başlangıç kataloğunu yönlendirir",
	},
	{
		"step": 2,
		"step_key": "plan",
		"image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&h=1600&q=80",
		"kicker_en": "Step 2 · Plan",
		"kicker_ar": "الخطوة 2 · الباقة",
		"kicker_tr": "Adım 2 · Plan",
		"title_en": "Pick the scale that fits you",
		"title_ar": "اختر الحجم الذي يناسبك",
		"title_tr": "Ölçeğine uygun planı seç",
		"subtitle_en": "Free, Growth, or Enterprise — beta is free; choose the tier that matches your catalog.",
		"subtitle_ar": "مجاني أو نمو أو مؤسسات — البيتا مجانية؛ اختر ما يناسب حجم كتالوجك.",
		"subtitle_tr": "Ücretsiz, Büyüme veya Kurumsal — beta ücretsiz; kataloğuna uygun olanı seç.",
		"bullet_1_icon": "📊",
		"bullet_1_en": "Catalog size guides the suggestion",
		"bullet_1_ar": "حجم الكتالوج يوجّه الاقتراح",
		"bullet_1_tr": "Katalog boyutu öneriyi yönlendirir",
		"bullet_2_icon": "💬",
		"bullet_2_en": "Support level from community to dedicated",
		"bullet_2_ar": "الدعم من المجتمع إلى مدير مخصص",
		"bullet_2_tr": "Topluluktan özel destek yöneticisine",
		"bullet_3_icon": "🆓",
		"bullet_3_en": "All plans free during beta",
		"bullet_3_ar": "كل الباقات مجانية أثناء البيتا",
		"bullet_3_tr": "Beta’da tüm planlar ücretsiz",
	},
	{
		"step": 3,
		"step_key": "look",
		"image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&h=1600&q=80",
		"kicker_en": "Step 3 · Look",
		"kicker_ar": "الخطوة 3 · المظهر",
		"kicker_tr": "Adım 3 · Görünüm",
		"title_en": "Choose a store look that sells",
		"title_ar": "اختر مظهراً يساعد على البيع",
		"title_tr": "Satan bir mağaza görünümü seç",
		"subtitle_en": "Niche templates ship with demo products and colors — change everything later.",
		"subtitle_ar": "القوالب المتخصصة تأتي بمنتجات وألوان تجريبية — يمكنك تغيير كل شيء لاحقاً.",
		"subtitle_tr": "Niş şablonlar demo ürün ve renklerle gelir — sonra her şeyi değiştirebilirsin.",
		"bullet_1_icon": "🎨",
		"bullet_1_en": "Fashion, electronics, beauty, home & more",
		"bullet_1_ar": "أزياء، إلكترونيات، تجميل، منزل والمزيد",
		"bullet_1_tr": "Moda, elektronik, güzellik, ev ve daha fazlası",
		"bullet_2_icon": "🖼️",
		"bullet_2_en": "Preview the live demo vibe",
		"bullet_2_ar": "معاينة أجواء المتجر التجريبي",
		"bullet_2_tr": "Canlı demo havasını önizle",
		"bullet_3_icon": "🔁",
		"bullet_3_en": "Swap theme anytime after launch",
		"bullet_3_ar": "بدّل المظهر في أي وقت بعد الإطلاق",
		"bullet_3_tr": "Açılıştan sonra temayı istediğin zaman değiştir",
	},
	{
		"step": 4,
		"step_key": "you",
		"image_url": "https://images.unsplash.com/photo-1556745753-b2904692b3cd?auto=format&fit=crop&w=1200&h=1600&q=80",
		"kicker_en": "Step 4 · You",
		"kicker_ar": "الخطوة 4 · أنت",
		"kicker_tr": "Adım 4 · Sen",
		"title_en": "Create your owner login",
		"title_ar": "أنشئ حساب المالك",
		"title_tr": "Mağaza sahibi girişini oluştur",
		"subtitle_en": "This email and password become your desk access for the new store.",
		"subtitle_ar": "هذا البريد وكلمة المرور يصبحان دخولك لإدارة المتجر الجديد.",
		"subtitle_tr": "Bu e-posta ve şifre yeni mağazanın yönetim girişi olur.",
		"bullet_1_icon": "👤",
		"bullet_1_en": "Full name on invoices & account",
		"bullet_1_ar": "الاسم الكامل على الفواتير والحساب",
		"bullet_1_tr": "Fatura ve hesapta ad soyad",
		"bullet_2_icon": "📱",
		"bullet_2_en": "Phone with country dial code",
		"bullet_2_ar": "جوال مع رمز الدولة",
		"bullet_2_tr": "Ülke kodlu telefon",
		"bullet_3_icon": "🔐",
		"bullet_3_en": "Secure password — min 8 characters",
		"bullet_3_ar": "كلمة مرور آمنة — 8 أحرف على الأقل",
		"bullet_3_tr": "Güvenli şifre — en az 8 karakter",
	},
	{
		"step": 5,
		"step_key": "address",
		"image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&h=1600&q=80",
		"kicker_en": "Step 5 · Address",
		"kicker_ar": "الخطوة 5 · العنوان",
		"kicker_tr": "Adım 5 · Adres",
		"title_en": "Claim your store address",
		"title_ar": "احجز عنوان متجرك",
		"title_tr": "Mağaza adresini kap",
		"subtitle_en": "yourbrand.flexloopers.com goes live after provisioning — custom domain later.",
		"subtitle_ar": "yourbrand.flexloopers.com يصبح جاهزاً بعد التجهيز — النطاق الخاص لاحقاً.",
		"subtitle_tr": "yourbrand.flexloopers.com kurulumdan sonra açılır — özel alan adı sonra.",
		"bullet_1_icon": "🔗",
		"bullet_1_en": "Pick a free subdomain",
		"bullet_1_ar": "اختر نطاقاً فرعياً متاحاً",
		"bullet_1_tr": "Boş bir alt alan seç",
		"bullet_2_icon": "🌐",
		"bullet_2_en": "Optional current website for later connect",
		"bullet_2_ar": "موقعك الحالي اختياري للربط لاحقاً",
		"bullet_2_tr": "İsteğe bağlı mevcut site — sonra bağlanır",
		"bullet_3_icon": "✅",
		"bullet_3_en": "We check availability instantly",
		"bullet_3_ar": "نتحقق من التوفر فوراً",
		"bullet_3_tr": "Müsaitliği anında kontrol ederiz",
	},
	{
		"step": 6,
		"step_key": "review",
		"image_url": "https://images.unsplash.com/photo-1556741533-411cf82e4e2d?auto=format&fit=crop&w=1200&h=1600&q=80",
		"kicker_en": "Step 6 · Review",
		"kicker_ar": "الخطوة 6 · مراجعة",
		"kicker_tr": "Adım 6 · İnceleme",
		"title_en": "Review and launch",
		"title_ar": "راجع وأطلق متجرك",
		"title_tr": "Gözden geçir ve başlat",
		"subtitle_en": "We provision storefront + ERP back office automatically — usually a few minutes.",
		"subtitle_ar": "نجهّز الواجهة والمحاسبة تلقائياً — عادة خلال دقائق.",
		"subtitle_tr": "Vitrin + ERP arka ofisi otomatik kurarız — genelde birkaç dakika.",
		"bullet_1_icon": "✅",
		"bullet_1_en": "Confirm company, plan, and look",
		"bullet_1_ar": "أكّد الشركة والباقة والمظهر",
		"bullet_1_tr": "Şirket, plan ve görünümü onayla",
		"bullet_2_icon": "⚡",
		"bullet_2_en": "One click starts provisioning",
		"bullet_2_ar": "نقرة واحدة تبدأ التجهيز",
		"bullet_2_tr": "Tek tıkla kurulum başlar",
		"bullet_3_icon": "🛡️",
		"bullet_3_en": "HTTPS secured before you go live",
		"bullet_3_ar": "تأمين HTTPS قبل الإطلاق",
		"bullet_3_tr": "Canlıya almadan önce HTTPS güvence",
	},
]


def seed_signup_aside_steps(force: bool = False) -> int:
	"""Create missing Signup Aside Step docs. Returns count created/updated."""
	if not frappe.db.exists("DocType", "Signup Aside Step"):
		return 0

	changed = 0
	for row in DEFAULTS:
		name = f"Step-{row['step']}"
		exists = frappe.db.exists("Signup Aside Step", name)
		if exists and not force:
			continue
		if exists:
			doc = frappe.get_doc("Signup Aside Step", name)
			doc.update(row)
			doc.enabled = 1
			doc.save(ignore_permissions=True)
		else:
			doc = frappe.get_doc({"doctype": "Signup Aside Step", "enabled": 1, **row})
			doc.insert(ignore_permissions=True)
		changed += 1
	frappe.db.commit()
	return changed
