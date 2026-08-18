(function () {
  function setLang(code) {
    if (!code) return;
    document.cookie = "sm_lang=" + code + "; path=/; max-age=31536000; SameSite=Lax";
    var url = new URL(window.location.href);
    url.searchParams.set("lang", code);
    window.location.href = url.toString();
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-sm-lang], a[data-sm-lang]");
    if (!btn) return;
    e.preventDefault();
    setLang(btn.getAttribute("data-sm-lang"));
  });

  var lang = document.documentElement.getAttribute("data-sm-lang");
  if (lang === "ar") {
    document.documentElement.setAttribute("dir", "rtl");
    document.body && document.body.classList.add("sm-rtl");
  }
})();
