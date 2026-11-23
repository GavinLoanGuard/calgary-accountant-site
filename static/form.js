// Intake form: keeps ad-click and campaign tags for the session, validates, posts JSON to /api/lead.
(function () {
  var KEYS = ["gclid", "utm_source", "utm_medium", "utm_campaign", "utm_term"];
  var q = new URLSearchParams(location.search);
  KEYS.forEach(function (k) {
    var v = q.get(k);
    try { if (v) sessionStorage.setItem(k, v); else v = sessionStorage.getItem(k); } catch (e) {}
    var el = document.getElementById(k);
    if (el && v) el.value = v.slice(0, 200);
  });
  var ref = document.getElementById("referrer");
  if (ref) ref.value = (document.referrer || "").slice(0, 300);

  var f = document.getElementById("leadform");
  if (!f) return;
  var msg = document.getElementById("formmsg");
  var btn = document.getElementById("submitbtn");
  var label = btn.textContent;

  f.addEventListener("input", function (e) {
    if (e.target.getAttribute("aria-invalid")) e.target.removeAttribute("aria-invalid");
  });

  f.addEventListener("submit", function (e) {
    e.preventDefault();
    msg.textContent = "";
    var bad = Array.prototype.filter.call(f.elements, function (el) { return el.willValidate && !el.checkValidity(); });
    if (bad.length) {
      bad.forEach(function (el) { el.setAttribute("aria-invalid", "true"); });
      msg.textContent = "Please complete the required fields, marked with an asterisk.";
      bad[0].focus();
      return;
    }
    var body = {};
    new FormData(f).forEach(function (v, k) {
      if (k === "services") (body.services = body.services || []).push(v);
      else body[k] = v;
    });
    btn.disabled = true;
    btn.textContent = "Sending…";
    fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); location.href = "/thank-you/"; })
      .catch(function () {
        btn.disabled = false;
        btn.textContent = label;
        msg.textContent = "Sorry, that didn’t go through. Please try again in a moment.";
      });
  });
})();
