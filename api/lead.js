// Vercel serverless function: receives the intake form and emails the lead to you via Resend.
// Required env vars (Vercel -> Project -> Settings -> Environment Variables):
//   RESEND_API_KEY   your Resend API key
//   LEAD_TO_EMAIL    where leads should be sent
//   LEAD_FROM_EMAIL  a verified sender on your domain, e.g. "Leads <leads@yourdomain.ca>"

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const clip = (v, n = 300) => String(v ?? "").trim().slice(0, n);
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function parseBody(req) {
  let b = req.body;
  if (typeof b === "string") { try { b = JSON.parse(b); } catch { b = null; } }
  return b && typeof b === "object" && !Array.isArray(b) ? b : {};
}

async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "method" });
  }
  const b = parseBody(req);

  // Honeypot: bots fill in the hidden field. Pretend success and send nothing.
  if (clip(b.company_website)) return res.status(200).json({ ok: true });

  const name = clip(b.name, 120);
  const email = clip(b.email, 200);
  if (!name || !EMAIL_RE.test(email) || b.consent_contact !== "yes") {
    return res.status(400).json({ ok: false, error: "invalid" });
  }

  const { RESEND_API_KEY, LEAD_TO_EMAIL, LEAD_FROM_EMAIL } = process.env;
  if (!RESEND_API_KEY || !LEAD_TO_EMAIL || !LEAD_FROM_EMAIL) {
    console.error("lead: missing RESEND_API_KEY / LEAD_TO_EMAIL / LEAD_FROM_EMAIL");
    return res.status(500).json({ ok: false, error: "config" });
  }

  const services = (Array.isArray(b.services) ? b.services : [b.services]).filter(Boolean).map((s) => clip(s, 100)).slice(0, 12);
  const insurance = b.consent_insurance === "yes";
  const rows = [
    ["Name", name], ["Email", email], ["Phone", clip(b.phone, 40)],
    ["Business", clip(b.business, 100)], ["Incorporated", clip(b.incorporated, 60)],
    ["Revenue", clip(b.revenue, 60)], ["Timing", clip(b.urgency, 60)],
    ["Needs", services.join("; ")], ["Message", clip(b.message, 2000)],
    ["Consent: contact + introduction after approval", "YES"],
    ["Consent: optional insurance contact", insurance ? "YES" : "no (do not contact about insurance)"],
    ["gclid", clip(b.gclid, 200)], ["utm_source", clip(b.utm_source, 200)], ["utm_medium", clip(b.utm_medium, 200)],
    ["utm_campaign", clip(b.utm_campaign, 200)], ["utm_term", clip(b.utm_term, 200)],
    ["Referrer", clip(b.referrer)], ["Received", new Date().toISOString()],
  ];
  const html = "<table cellpadding='6' style='font-family:Arial,sans-serif;font-size:14px;border-collapse:collapse'>" +
    rows.map(([k, v]) => `<tr><td style='border-bottom:1px solid #ddd'><b>${esc(k)}</b></td><td style='border-bottom:1px solid #ddd;white-space:pre-wrap'>${esc(v)}</td></tr>`).join("") +
    "</table>";
  const text = rows.map(([k, v]) => `${k}: ${v}`).join("\n");

  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        from: LEAD_FROM_EMAIL,
        to: LEAD_TO_EMAIL.split(",").map((s) => s.trim()).filter(Boolean),
        reply_to: email,
        subject: `New accountant lead: ${name} (${clip(b.business, 60) || "n/a"})${insurance ? " [insurance OK]" : ""}`,
        html, text,
      }),
      signal: AbortSignal.timeout(8000),
    });
    if (!r.ok) throw new Error("resend " + r.status);
    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error("lead email failed", e && e.message);
    return res.status(502).json({ ok: false, error: "send" });
  }
}

module.exports = handler;
