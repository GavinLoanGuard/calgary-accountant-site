#!/usr/bin/env python3
"""Static site generator for the Calgary accountant-introduction site.

Edit the CONFIG block, then run:  python3 build.py
Output goes to ./dist. Vercel runs this automatically (see vercel.json) and deploys ./api alongside.
Design rules live in DESIGN.md.
"""
import json, os, shutil
from html import escape

# ----------------------------------------------------------------- CONFIG
BRAND = "Calgary Accountant Match"          # placeholder - change when the domain is chosen
WORDMARK = ("Calgary", "Accountant Match")  # small caps line, serif line
DOMAIN = "https://www.example.ca"           # placeholder - the real domain, no trailing slash
PHONE = ""                                  # optional, e.g. "(403) 555-0100"
CONTACT_EMAIL = ""                          # optional, shown on privacy page and 404, e.g. "hello@yourdomain.ca"
OPERATOR = "Gavin Dyer"
OPERATOR_NOTE = ("This site is operated by Gavin Dyer, an independent Alberta-licensed life and "
                 "living-benefits insurance broker. It is an introduction service, not an "
                 "accounting firm or a law firm.")
HEADSHOT = ""                               # optional, e.g. "/img/gavin.jpg" (put the file in static/img/)
GADS_ID = ""                                # e.g. "AW-1234567890" - leave blank until ready
GADS_LEAD_LABEL = ""                        # e.g. "AW-1234567890/AbCdEf" for the thank-you conversion
# ------------------------------------------------------------------------

OUT = "dist"
STATIC = "static"
FORM = "/find-an-accountant/"

NAV = [("Physicians", "/accountant-for-doctors-calgary/"),
       ("Consultants", "/accountant-for-consultants-calgary/"),
       ("Corporate tax", "/corporate-tax-accountant-calgary/"),
       ("Planning", "/business-tax-planning-calgary/"),
       ("How it works", "/how-it-works/")]

# =========================================================== PRIMITIVES

def head(title, desc, path, ld=None, noindex=False):
    gtag = ""
    if GADS_ID:
        gtag = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GADS_ID}"></script>'
                '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}'
                f'gtag("js",new Date());gtag("config","{GADS_ID}");</script>')
    robots = '<meta name="robots" content="noindex,follow">' if noindex else ""
    lds = "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>"
                  for x in (ld or []))
    return f"""<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{DOMAIN}{path}">{robots}
<meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{DOMAIN}{path}">
<meta property="og:locale" content="en_CA"><meta name="theme-color" content="#f3efe6">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/newsreader-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">{gtag}{lds}
</head><body><a class="skip" href="#main">Skip to content</a>"""


def header(path):
    def link(t, u):
        cur = ' aria-current="page"' if u == path else ""
        return f'<a href="{u}"{cur}>{escape(t)}</a>'
    links = "".join(link(t, u) for t, u in NAV)
    return f"""<header class="top"><div class="wrap">
<a class="wm" href="/" aria-label="{escape(BRAND)}, home"><small>{escape(WORDMARK[0])}</small><span>{escape(WORDMARK[1])}</span></a>
<nav class="nav" aria-label="Main">{links}<a class="req" href="{FORM}">Request an introduction</a></nav>
<details class="menu"><summary>Menu</summary><nav aria-label="Main (mobile)">{links}<a class="req" href="{FORM}">Request an introduction</a></nav></details>
</div></header><main id="main">"""


def footer():
    svc = "".join(f'<li><a href="/{p["slug"]}/">{escape(p["nav"])}</a></li>' for p in PAGES)
    ph = f'<p>{escape(PHONE)}</p>' if PHONE else ""
    return f"""</main><footer class="foot"><div class="wrap">
<div class="foot-g">
<div><p class="wm wm-foot"><small>{escape(WORDMARK[0])}</small><span>{escape(WORDMARK[1])}</span></p>
<p>Introductions to accountants for incorporated professionals and owner-managers in Calgary.</p>{ph}
<p><a class="foot-req" href="{FORM}">Request an introduction</a></p></div>
<div><p class="foot-h">Situations</p><ul>{svc}</ul></div>
<div><p class="foot-h">The service</p><ul><li><a href="/how-it-works/">How it works</a></li>
<li><a href="{FORM}">Request an introduction</a></li><li><a href="/privacy/">Privacy and consent</a></li></ul></div>
</div>
<div class="fine"><p>{escape(OPERATOR_NOTE)} Everything on this site is general information, not tax, legal,
accounting or insurance advice. Any accounting firm you're introduced to is independent, sets its own fees and is
responsible for its own work. No tax outcome is promised or implied.</p><p>© {escape(BRAND)}</p></div>
</div></footer></body></html>"""


def label(n, text):
    num = f'<span class="n">{n:02d}</span>' if n else ""
    return f'<p class="label">{num}{escape(text)}</p>'


def sec(n, lab, body, cls=""):
    return f"""<section class="sec {cls}"><div class="wrap g"><div class="sec-label">{label(n, lab)}</div>
<div class="sec-body">{body}</div></div></section>"""


def h2(t):
    return f"<h2>{t}</h2>" if t else ""


def statement(text):
    return f"""<section class="statement"><div class="wrap g"><div></div><p>{text}</p></div></section>"""


def table(headers, rows, note=""):
    th = "".join(f'<th scope="col">{h}</th>' for h in headers)
    trs = ""
    for r in rows:
        cells = f'<th scope="row">{r[0]}</th>' + "".join(
            f'<td data-h="{escape(headers[i + 1])}">{c}</td>' for i, c in enumerate(r[1:]))
        trs += f"<tr>{cells}</tr>"
    n = f'<p class="note">{note}</p>' if note else ""
    return f'<div class="tbl-wrap"><table class="tbl cols-{len(headers)}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>{n}'


def numbered(items):
    lis = "".join(f"<li><div><h3>{h}</h3><p>{p}</p></div></li>" for h, p in items)
    return f'<ol class="num">{lis}</ol>'


def dash(items):
    return '<ul class="dash">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def cols(items):
    return '<div class="cols3">' + "".join(f"<div><h3>{h}</h3><p>{p}</p></div>" for h, p in items) + "</div>"


def stages(items):
    return '<div class="stages">' + "".join(
        f'<div><p class="stage-k">{k}</p><h3>{h}</h3>{dash(lst)}</div>' for k, h, lst in items) + "</div>"


def qa(faqs):
    return '<div class="qas">' + "".join(f'<div class="qa"><h3>{q}</h3><p>{a}</p></div>' for q, a in faqs) + "</div>"


def closer(text, button="Request an introduction"):
    return f"""<section class="closer"><div class="wrap"><div class="closer-g"><p class="big">{text}</p>
<div><a class="btn" href="{FORM}">{escape(button)}</a><p class="small">Free. Nothing is shared without your approval.</p></div>
</div></div></section>"""


def related(slugs):
    items = "".join(f'<li><a href="/{s}/">{escape(BY_SLUG[s]["nav"])}</a></li>' for s in slugs)
    return f'<aside class="related"><div class="wrap"><p class="label">Also relevant</p><ul>{items}</ul></div></aside>'


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").replace("&nbsp;", " ")


def ld_faq(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs]}


def ld_crumbs(name, path):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": DOMAIN + path}]}


def write(path, html):
    full = os.path.join(OUT, "index.html") if path == "/" else os.path.join(OUT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


def headshot_html():
    if not HEADSHOT:
        return ""
    return (f'<figure class="headshot"><img src="{escape(HEADSHOT)}" width="320" height="400" '
            f'alt="{escape(OPERATOR)}" loading="lazy"><figcaption>{escape(OPERATOR)}</figcaption></figure>')

# ============================================================== CONTENT
# Each page: slug, nav, title, desc, h1, lead, blocks (rendered in order), faqs, closer, related.
# Blocks are ("kind", ...) tuples. Each page deliberately uses a different mix.

PAGES = [
 dict(slug="accountant-for-doctors-calgary", nav="Physicians and medical professionals",
  blurb="Professional corporations, the salary and dividend mix, and what happens to what stays inside.",
  title="Accountant for Physicians &amp; Doctors in Calgary",
  desc="An accountant for physicians in Calgary who understands medical professional corporations: pay mix, retained earnings, passive income and long-term planning. Free introduction.",
  h1="An accountant for physicians in Calgary who knows professional corporations",
  lead="Physicians earn well, start late and usually incorporate early. An accountant for physicians in Calgary "
       "should understand a medical professional corporation from the inside: how billings flow into it, how you draw "
       "from it, and what happens to the money that stays behind.",
  blocks=[
   ("statement", "The corporation isn’t the plan. It’s the container the plan lives in."),
   ("prose", "Who this is for", "Family doctors, specialists, and the last year of residency",
    "<p>Family physicians and specialists billing fee-for-service, on an alternative relationship plan, or a mix of "
    "the two. Most already have a professional corporation; some are deciding whether to set one up. Residents in "
    "their final year are welcome too. It’s a good time to have the conversation, before the billings start.</p>"
    "<p>Dentists and other regulated health professionals with a professional corporation face most of the same "
    "questions, and the same accountants usually look after them.</p>"),
   ("table", "Inside the corporation", "The questions a physician’s accountant should be raising",
    ["Question", "Why it matters"],
    [["Salary, dividends, or both?", "Salary creates RRSP room and CPP contributions; dividends don’t. The right mix depends on what you’re saving for and what you actually spend."],
     ["How much to leave in the company?", "Money left inside is taxed at a lower corporate rate until you take it out. That makes the corporation a useful place to save, up to a point."],
     ["What happens as investments grow?", "Once passive investment income inside a corporation passes $50,000 a year, access to the small business rate starts to shrink. Better to plan for that than discover it."],
     ["Family members as shareholders?", "The rules for medical professional corporations limit who can hold shares, and the 2018 tax-on-split-income rules cut the benefit of paying dividends to family. Worth a look if your structure is older than that."],
     ["Practice changes", "A new clinic, going part-time, parental leave, or a move out of province each changes the answer to most of the questions above."]],
    "General information only. Your accountant will tell you how each point applies to you."),
   ("numbered", "What to look for", "Three things to check in a first meeting",
    [("They already look after physicians", "Ask roughly how many medical professional corporations the firm handles. You want this to be routine for them."),
     ("They talk about the next ten years, not just this year-end", "A good physician’s accountant will ask about retirement age, family, and when you might want to slow down."),
     ("They’ll work with your other advisors", "Your lawyer, your investment advisor and, if you have one, your insurance advisor should be pulling in the same direction.")]),
  ],
  faqs=[("Should a physician incorporate?", "Usually, once income comfortably exceeds what you need to live on. But it depends on spending, family, debt and goals, which is exactly the conversation to have with an accountant who works with professional corporations."),
        ("I’m still a resident. Is it too early?", "No. The final year of residency is a good time to understand the options, so the corporation is set up properly before you start billing."),
        ("Is my information shared automatically?", "No. Nothing goes to an accounting firm until you’ve agreed to an introduction to that specific firm.")],
  closer="Tell us where your practice is now. We’ll suggest an accountant who looks after physicians, and nothing goes anywhere until you say so.",
  related=["business-tax-planning-calgary", "holding-company-accountant-calgary", "change-accountants-calgary"]),

 dict(slug="accountant-for-consultants-calgary", nav="Consultants and contractors",
  blurb="Owner pay, reasonable expenses, and the personal services business question.",
  title="Accountant for Consultants &amp; Contractors in Calgary",
  desc="An accountant for incorporated consultants and contractors in Calgary: owner pay, expenses, retained earnings and personal services business risk. Free introduction.",
  h1="An accountant for incorporated consultants and contractors in Calgary",
  lead="If you bill through your own corporation, the company is the business and you’re its only employee. An "
       "accountant for consultants in Calgary should help with three things: how you pay yourself, what the company can "
       "reasonably deduct, and whether your contracts risk being treated as a personal services business.",
  blocks=[
   ("split", "The PSB question", "Are you an incorporated employee?",
    "<p>If the Canada Revenue Agency decides your corporation is really standing in for an employee of your client, "
    "it’s classed as a <em>personal services business</em>. The company loses the small business deduction, pays tax "
    "at a higher rate, and can deduct very little.</p><p>It’s judged on the facts of each engagement. So the time to "
    "look at it is when you sign a contract, not when CRA asks.</p>",
    "Worth raising with an accountant if",
    ["One client pays most of your income",
     "They set your hours and direct how you work",
     "Your contract reads like an employment agreement",
     "You’d plainly be an employee if the corporation weren’t there"]),
   ("prose", "Who this is for", "Consultants who bill through a corporation",
    "<p>Engineers, geoscientists, project managers, IT and data consultants, and the many energy-sector specialists "
    "in Calgary who went independent and incorporated. Some have one long contract; others juggle several clients. "
    "Most have cash building up in the company and no clear plan for it yet.</p>"),
   ("table", "Common decisions", "Where a good accountant earns the fee",
    ["Decision", "What to think about"],
    [["How to pay yourself", "Salary builds RRSP room and CPP; dividends are simpler and don’t. Many consultants use a mix, and the mix should change as your income does."],
     ["What to do with retained earnings", "Leave it in the company, invest it there, or move it to a holding company. Each has trade-offs on tax, flexibility and risk."],
     ["Expenses", "Home office, vehicle, equipment and training can be legitimate. They need to be reasonable, business-related and documented."],
     ["Between contracts", "A gap in work changes how much you should draw and when. Plan the gap before it arrives."]]),
  ],
  faqs=[("I’m a one-person corporation. Is an accountant worth it?", "Usually. The decisions about pay, expenses and retained earnings are the same as for a larger company, and getting them wrong costs more than the fee."),
        ("Can you tell me if I’m a personal services business?", "No. That’s an assessment for an accountant or tax lawyer, based on your contracts and how you actually work. We’ll introduce you to someone who can look at it."),
        ("How quickly can I get an introduction?", "We usually reply within one business day of receiving your details.")],
  closer="Send a few details about your contracts and your corporation. We’ll suggest an accountant who works with consultants.",
  related=["holding-company-accountant-calgary", "incorporation-tax-setup-calgary", "corporate-tax-accountant-calgary"]),

 dict(slug="corporate-tax-accountant-calgary", nav="Corporate tax",
  blurb="Year-end, the T2, instalments, and a planning conversation before the books close.",
  title="Corporate Tax Accountant in Calgary",
  desc="A corporate tax accountant in Calgary for owner-managed corporations: year-end, T2 returns, instalments and pay planning before the books close. Free introduction.",
  h1="A corporate tax accountant in Calgary who does more than file the T2",
  lead="If your corporation’s year-end is a box of receipts and a filing deadline, you’re paying a corporate tax "
       "accountant in Calgary to do the minimum. Tell us about the company and we’ll introduce you to a firm that "
       "looks after owner-managed corporations like yours.",
  blocks=[
   ("prose", "Who this is for", "Owner-managed corporations",
    "<p>Usually one to three shareholders, with the owner’s personal finances and the company’s tangled together in "
    "the normal way. Revenue anywhere from a few hundred thousand dollars to a few million. There’s often a "
    "bookkeeper or cloud software in place already. What’s missing is someone looking at the whole picture.</p>"),
   ("table", "The year, not the deadline", "What a corporate tax accountant should do, and when",
    ["When", "What should happen"],
    [["Before year-end", "A conversation about pay: how much salary, how much dividend, and whether to declare a bonus before the books close."],
     ["At year-end", "Financial statements and the T2 corporate return, due six months after your fiscal year-end."],
     ["After filing", "A short review of what the numbers say, what changes next year, and what’s building up inside the company."],
     ["Through the year", "Instalments, GST returns and payroll remittances handled or checked, so nothing arrives as a surprise from CRA."]],
    "Any tax owing is generally due before the return is: two or three months after year-end, depending on the corporation."),
   ("numbered", "What to look for", "Questions to ask before you engage a firm",
    [("How many corporations like mine do you look after?", "You want a firm for which your situation is ordinary, not a stretch."),
     ("Who will I actually deal with?", "A named person, and an honest answer about how quickly they usually reply."),
     ("What’s in the fee, and what isn’t?", "Year-end, the T2, a planning meeting, CRA letters. Get the scope in writing."),
     ("Will you work with my lawyer?", "Restructuring, shareholder agreements and estate plans all need the accountant and the lawyer in the same conversation.")]),
  ],
  faqs=[("What does a corporate tax accountant do?", "Prepares your corporation’s financial statements and T2 return. The good ones also advise on how you pay yourself, when to time income and expenses, and how the structure should change as the company grows."),
        ("How much does a corporate accountant cost in Calgary?", "It depends on how complex the company is, how clean the books are, and what’s included. The firm sets its fee, not us. Ask for a written quote."),
        ("When should I switch?", "Common triggers: the company has grown, you’ve added a holding company or a shareholder, a sale is on the horizon, or you only hear from your accountant at filing time.")],
  closer="Tell us about your corporation and what you’d like from an accountant that you’re not getting now.",
  related=["holding-company-accountant-calgary", "change-accountants-calgary", "business-tax-planning-calgary"]),

 dict(slug="business-tax-planning-calgary", nav="Tax, estate and succession planning",
  blurb="Taking money out, holding what you don’t spend, and what happens when you stop.",
  title="Business Tax, Estate &amp; Succession Planning in Calgary",
  desc="Business tax planning, estate planning and succession planning in Calgary for incorporated owners and professionals. Get introduced to an accountant who plans ahead.",
  h1="Business tax, estate and succession planning in Calgary",
  lead="Business tax planning in Calgary, for an owner-manager, comes down to three questions asked at different "
       "points in life: how to take money out of the company, how to hold what you don’t spend, and what happens to "
       "the company when you stop. Estate and succession planning answer the last one, and need the most lead time.",
  blocks=[
   ("stages", "Three stages", "The planning changes as the company matures",
    [("Stage one", "Building", ["Salary and dividend mix", "RRSPs and saving inside the company", "Keeping the books clean enough to plan with"]),
     ("Stage two", "Holding", ["A holding company for surplus cash", "Investments inside the corporation and the passive income limits", "Who owns the shares, and why"]),
     ("Stage three", "Leaving", ["Selling to a third party or a partner", "Passing the company to family", "An estate freeze, and what happens on death"])]),
   ("statement", "Start a succession plan years before you need it. Most of the useful options take time to put in place."),
   ("prose", "Estates", "Private company shares and the risk of paying twice",
    "<p>When an owner dies, their shares are generally treated as if they were sold at fair market value. Without "
    "planning, the same value can end up taxed twice: once in the owner’s final return and again when the money "
    "comes out of the corporation.</p><p>Accountants and lawyers have well-established ways to prevent that. They "
    "work best when they’re set up in advance and coordinated with the will, the shareholder agreement and any "
    "corporate-owned life insurance.</p>"),
   ("dash", "Who this is for", "Owners with a decade or less to plan",
    ["Owners thinking about a sale, retirement, or a transfer to family or partners",
     "High-income professionals who want the tax plan and the estate plan to match",
     "Corporations holding significant retained earnings or investments",
     "Partners in a business with no shareholder agreement, or an old one"]),
   ("numbered", "What to look for", "Signs of an accountant who plans",
    [("They bring up the topic before you do", "Planning shouldn’t depend on you knowing what to ask."),
     ("They put it in writing", "A short written plan with agreed next steps, reviewed each year."),
     ("They’re comfortable in a room with your lawyer", "Succession and estate work is a team effort. An accountant who works alone here is a warning sign.")]),
  ],
  faqs=[("How early should I start a succession plan?", "Ideally several years ahead. Many of the tax and structural options need time to set up, and some need the company to meet conditions for a period before a sale."),
        ("Is estate planning an accountant’s job?", "Partly. The accountant handles the tax side; a lawyer drafts the will and legal documents. The best results come when they work together."),
        ("Can you introduce me to a lawyer as well?", "Yes, if you ask. Nothing is shared with anyone without your agreement.")],
  closer="Tell us roughly where you are: building, holding or getting ready to leave. We’ll suggest an accountant who does this kind of planning.",
  related=["holding-company-accountant-calgary", "accountant-for-doctors-calgary", "corporate-tax-accountant-calgary"]),

 dict(slug="holding-company-accountant-calgary", nav="Holding companies",
  blurb="Moving surplus out of the operating company, and the rules that come with it.",
  title="Holding Company Accountant in Calgary",
  desc="A holding company accountant in Calgary for owners with surplus cash, a sale ahead or family succession in mind. Structure, inter-corporate dividends and planning. Free introduction.",
  h1="Holding company accountant in Calgary",
  lead="A good holding company accountant in Calgary will start with one question: what is the holding company "
       "meant to solve? Moving surplus cash away from the operating company’s risk, preparing for a sale, or bringing "
       "family in over time are good answers. “My neighbour has one” isn’t.",
  blocks=[
   ("structure", "A typical structure", "The simple version"),
   ("table", "Reasons and catches", "Why owners set one up, and the catch with each",
    ["Reason", "The catch"],
    [["Move surplus out of the operating company, away from its business risk", "Dividends between connected corporations are often tax-free, but anti-avoidance rules can apply. It has to be done properly."],
     ["Get ready to sell", "Claiming the lifetime capital gains exemption on a share sale means keeping the operating company clear of excess cash and investments. That takes planning well before the sale."],
     ["Invest inside a corporation", "The passive income limits look at associated corporations together, so a holding company doesn’t get around them."],
     ["Family and succession", "Often involves a family trust or an estate freeze, which means a lawyer as well as an accountant."]]),
   ("dash", "Who this is for", "Owners with more than one moving part",
    ["A profitable operating company with cash it doesn’t need",
     "More than one corporation, or more than one shareholder",
     "A sale, a partner buy-out or a family transfer somewhere on the horizon"]),
   ("numbered", "What to look for", "In an accountant for a multi-company structure",
    [("Hands-on experience with holding companies", "Ask how many they maintain, not whether they’ve set one up."),
     ("They explain the costs as well as the benefits", "Two companies mean two sets of statements and two returns."),
     ("They work alongside a corporate lawyer", "Restructuring is legal work as much as tax work.")]),
  ],
  faqs=[("Do I need a holding company?", "Not always. It depends on how much surplus you have, what you plan to do with it, and whether a sale or family transfer is likely. An accountant and a lawyer should assess it together."),
        ("Do I need a lawyer as well?", "Usually. Setting up or reorganising a structure involves legal documents as well as tax advice. We can introduce you to a corporate lawyer too."),
        ("What does it cost to run one?", "There are extra accounting and filing costs every year. A good advisor will tell you what they are before you commit.")],
  closer="Tell us about your companies and what you’re hoping a holding company would do.",
  related=["business-tax-planning-calgary", "corporate-tax-accountant-calgary", "accountant-for-consultants-calgary"]),

 dict(slug="incorporation-tax-setup-calgary", nav="Incorporating",
  blurb="Whether to incorporate, and setting it up so the first year-end isn’t a mess.",
  title="Incorporation &amp; Tax Set-Up Accountant in Calgary",
  desc="Thinking about incorporating in Alberta? Get introduced to a Calgary accountant for incorporation and tax set-up: whether it makes sense, registrations and your first year.",
  h1="Incorporation and tax set-up in Calgary: decide first, then file",
  lead="Filing articles of incorporation in Alberta takes an afternoon. Deciding whether to incorporate, and setting "
       "the company up so the first year-end isn’t a mess, takes a conversation with an accountant. We’ll introduce "
       "you to a Calgary firm that handles incorporation and tax set-up for professionals and small businesses.",
  blocks=[
   ("table", "Should you?", "When incorporating tends to make sense",
    ["", "Tends to make sense", "Often doesn’t, yet"],
    [["Income", "You earn more than you need to live on and can leave the rest in the company", "You need all of it personally"],
     ["Stability", "Revenue is steady and growing", "Income is modest or irregular"],
     ["Plans", "You expect to hire, grow or eventually sell", "It’s a side business or a short-term contract"],
     ["Cost", "The tax deferral outweighs a second set of accounts", "Extra accounting and filing costs would eat the benefit"]],
    "Incorporating doesn’t remove professional liability. Ask a lawyer what it does and doesn’t protect."),
   ("numbered", "First-year checklist", "If you go ahead",
    [("Choose a fiscal year-end", "It doesn’t have to be December 31. Your accountant may suggest something that suits your cash flow and their workload."),
     ("Register what you need with CRA", "A business number, a GST account once taxable sales pass the $30,000 small-supplier threshold (or earlier, voluntarily), and payroll if you’ll pay yourself a salary."),
     ("Keep the money separate from day one", "A business bank account and card. Mixing personal and company spending is the most common first-year mess."),
     ("Set up bookkeeping your accountant can see", "Cloud software they can log into beats a spreadsheet emailed at year-end."),
     ("Decide on shares before you issue them", "Who owns what, and in which classes. It’s far easier to get right now than to change later.")]),
   ("prose", "Who this is for", "Self-employed and about to incorporate",
    "<p>Self-employed professionals and contractors weighing whether it’s time, founders setting up a new Alberta "
    "corporation, and owners who incorporated recently and want someone to check it was done properly.</p>"),
  ],
  faqs=[("Do I need an accountant to incorporate?", "Not legally. But an accountant can tell you whether it makes sense yet, and help you avoid the set-up mistakes that cost money to unwind."),
        ("Can you incorporate my company for me?", "No. We’re not a law firm or an accounting firm. We introduce you to professionals who can advise on it or do it."),
        ("What happens after I send the form?", "We read your details, may ask a question or two, and suggest a firm. If you agree, we introduce you.")],
  closer="Tell us what you do and roughly what you earn. We’ll suggest an accountant who can tell you whether incorporating makes sense yet.",
  related=["small-business-accountant-calgary", "accountant-for-consultants-calgary", "corporate-tax-accountant-calgary"]),

 dict(slug="small-business-accountant-calgary", nav="Small businesses",
  blurb="For owners who’ve outgrown the shoebox, the bookkeeper or the accountant who’s gone quiet.",
  title="Small Business Accountant in Calgary",
  desc="A small business accountant in Calgary for incorporated owners: first year-end, GST, bookkeeping review and owner pay. Free introduction to a firm that fits.",
  h1="A small business accountant in Calgary, for owners who’ve outgrown the shoebox",
  lead="Owners usually look for a small business accountant in Calgary at one of three moments: they’ve just "
       "incorporated, their bookkeeper has done all they can, or their current accountant has stopped returning "
       "calls. A good one gets the first year right and then keeps an eye on what comes next.",
  blocks=[
   ("cols", "Three moments", "Which one sounds like you?",
    [("Just incorporated", "You need the first year-end done properly, GST and payroll set up, and a sensible plan for paying yourself."),
     ("Outgrown the bookkeeper", "The books are tidy, but nobody is telling you what they mean or what to do differently."),
     ("Your accountant has gone quiet", "Slow replies, surprise invoices, and a phone call once a year when something is due.")]),
   ("prose", "Software isn’t an accountant", "What the bookkeeping app won’t tell you",
    "<p>Cloud bookkeeping software is good at recording transactions. It won’t tell you whether to pay yourself a "
    "salary, whether the truck belongs in the company, or that you need to register for GST once taxable sales pass "
    "$30,000 over four consecutive quarters.</p><p>An accountant who reviews your books a few times a year catches "
    "these early, which is a lot cheaper than fixing them at year-end.</p>"),
   ("dash", "A good fit", "What to look for",
    ["Works with businesses your size, not just larger clients",
     "Gives you a named contact who replies",
     "Logs into your cloud books rather than asking for exports",
     "Quotes the fee before starting"]),
  ],
  faqs=[("Do I need an accountant if I use accounting software?", "Software records what happened. An accountant checks it, prepares your corporate return, and advises on the decisions software can’t make."),
        ("Can you help if I only need bookkeeping?", "We focus on accountants for incorporated businesses. If bookkeeping is all you need, say so on the form and we’ll tell you honestly whether we can help."),
        ("Is there a cost?", "Not to you. The firm you engage sets and bills its own fees.")],
  closer="Tell us which of the three moments you’re in. We’ll suggest a firm that fits a business your size.",
  related=["incorporation-tax-setup-calgary", "corporate-tax-accountant-calgary", "change-accountants-calgary"]),

 dict(slug="change-accountants-calgary", nav="Changing accountants",
  blurb="How a switch works in practice. The new firm does most of the work.",
  title="Changing Accountants in Calgary: How a Switch Works",
  desc="Thinking about changing accountants in Calgary? How a switch works, when to do it, and an introduction to a firm that fits your corporation.",
  h1="Changing accountants in Calgary is less awkward than you think",
  lead="Most owners who want to change accountants in Calgary put it off because of the handover. In practice the "
       "new firm does most of the work, and you don’t need to have a difficult conversation.",
  blocks=[
   ("numbered", "How a switch works", "Five steps, most of them not yours",
    [("You agree a scope and fee with the new firm", "Talk to one or two firms. Get what’s included in writing."),
     ("The new firm contacts your previous accountant", "Professional rules for CPAs generally expect this before a new client is taken on. You don’t have to make the call."),
     ("You authorize the new firm with CRA", "Through Represent a Client, so they can see your corporation’s accounts and correspondence."),
     ("Last year’s files come across", "Prior financial statements, returns and the balances the new firm needs to carry forward."),
     ("The new firm picks up at your next deadline", "Tell them your fiscal year-end and anything due soon, and they’ll plan around it.")]),
   ("table", "Good reasons", "Signs it may be time",
    ["Sign", "What it usually means"],
    [["You only hear from them at filing time", "Compliance is being done. Planning isn’t."],
     ["Questions take weeks to answer", "You’ve become a small client at a busy firm."],
     ["The company has changed and the advice hasn’t", "A holding company, a new shareholder or a sale ahead needs different expertise."],
     ["Invoices are a surprise", "There’s no agreed scope. That’s fixable, but often a sign of the wider relationship."]]),
   ("prose", "Timing", "When to switch",
    "<p>The easiest time is just after a year-end has been filed, when there’s nothing in progress. But switching "
    "mid-year is common and perfectly manageable. The important thing is that the new firm knows your deadlines "
    "from the start.</p>"),
  ],
  faqs=[("Do I have to tell my current accountant?", "It’s courteous to let them know, but the new firm will normally handle the handover. Our introduction doesn’t contact your current accountant."),
        ("Will I miss a deadline if I switch mid-year?", "Not if the new firm knows your dates. Mention them on the form and again in your first meeting."),
        ("What if my books are a mess?", "Say so. Catch-up work is routine for most firms; it just affects the first-year quote.")],
  closer="Tell us what isn’t working with your current accountant. We’ll suggest a firm that’s a better fit.",
  related=["corporate-tax-accountant-calgary", "small-business-accountant-calgary", "accountant-for-doctors-calgary"]),
]
BY_SLUG = {p["slug"]: p for p in PAGES}

STRUCTURE = """<figure class="struct"><div class="struct-row">
<div class="node"><strong>You</strong><span>Owner and shareholder</span></div><div class="link" aria-hidden="true"></div>
<div class="node"><strong>Holding company</strong><span>Holds surplus cash and investments</span></div><div class="link" aria-hidden="true"></div>
<div class="node node-op"><strong>Operating company</strong><span>Earns the revenue, carries the business risk</span></div></div>
<figcaption>Simplified. Real structures often add a family trust or a second operating company, and need legal as well as tax advice.</figcaption></figure>"""

# ================================================================ PAGES

def render_block(n, b):
    kind = b[0]
    if kind == "statement":
        return statement(b[1]), n
    n += 1
    if kind == "prose":
        _, lab, title, body = b; return sec(n, lab, h2(title) + body), n
    if kind == "table":
        _, lab, title, hdr, rows, *note = b
        return sec(n, lab, h2(title) + table(hdr, rows, note[0] if note else "")), n
    if kind == "numbered":
        _, lab, title, items = b; return sec(n, lab, h2(title) + numbered(items)), n
    if kind == "dash":
        _, lab, title, items = b; return sec(n, lab, h2(title) + dash(items)), n
    if kind == "cols":
        _, lab, title, items = b; return sec(n, lab, h2(title) + cols(items)), n
    if kind == "stages":
        _, lab, title, items = b; return sec(n, lab, h2(title) + stages(items)), n
    if kind == "structure":
        _, lab, title = b; return sec(n, lab, h2(title) + STRUCTURE), n
    if kind == "split":
        _, lab, title, body, side_h, side = b
        inner = (h2(title) + f'<div class="split"><div>{body}</div>'
                 f'<div class="split-side"><p class="label">{escape(side_h)}</p>{dash(side)}</div></div>')
        return sec(n, lab, inner), n
    raise ValueError(kind)


def page_hero(crumb, h1, lead):
    c = (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span>'
         f'<span aria-current="page">{escape(crumb)}</span></nav>') if crumb else ""
    return f"""<section class="phero"><div class="wrap">{c}<h1>{h1}</h1><p class="lead">{lead}</p>
<p class="phero-cta"><a class="btn" href="{FORM}">Request an introduction</a><span>Free. About two minutes.</span></p></div></section>"""


def build_service(p):
    path = f"/{p['slug']}/"
    body, n = "", 0
    for b in p["blocks"]:
        html, n = render_block(n, b)
        body += html
    n += 1
    body += sec(n, "Questions", h2("") + qa(p["faqs"]) +
                '<p class="note">General information only, not tax, legal or accounting advice.</p>')
    html = head(strip_tags(p["title"]) + f" | {BRAND}", p["desc"], path,
                [ld_faq(p["faqs"]), ld_crumbs(strip_tags(p["nav"]), path)])
    html += header(path) + page_hero(strip_tags(p["nav"]), p["h1"], p["lead"]) + body
    html += closer(p["closer"]) + related(p["related"]) + footer()
    write(path, html)


HOME_FAQS = [
 ("Is this an accounting firm?", "No. It’s an introduction service. We find out what you need, suggest an accountant we think fits, and introduce you if you agree. The accounting work, and the bill for it, come from that firm."),
 ("What does it cost?", "Nothing to you. The firm you engage sets its own fees, and you should get them in writing before you start."),
 ("Who sees my details?", f"{OPERATOR}, who runs this site. Nothing goes to an accounting firm until you’ve agreed to an introduction to that specific firm."),
 ("Why is an insurance broker running an accountant introduction service?", "Because the people who most need a good accountant, incorporated professionals with real planning questions, are the people Gavin already works with. Good accountants are hard to find, and introducing people to one is useful. If you’d also like to hear about corporate insurance, there’s a separate box for that on the form. Leave it blank and you won’t."),
 ("Is it only for physicians and consultants?", "No. They’re a focus because their questions overlap, but any incorporated owner in Calgary is welcome to ask."),
]


def build_home():
    toc = "".join(f'<li><a href="/{p["slug"]}/"><span class="t">{escape(p["nav"])}</span><span class="d">{p["blurb"]}</span></a></li>' for p in PAGES)
    asks = ["How much of this year’s income do you actually need personally?",
            "What’s the plan for the cash building up in the corporation?",
            "Who owns the shares, and does that still make sense?",
            "If you stopped working in ten years, what happens to the company?"]
    asks_html = "".join(f"<li>{a}</li>" for a in asks)
    compare = table(["", "A filing accountant", "A planning accountant"], [
        ["When you hear from them", "When something is due", "Before year-end, and when something changes"],
        ["Salary or dividends", "Whatever you did last year", "Reviewed against what you spend and what you’re saving for"],
        ["Cash left in the company", "A number on the balance sheet", "A plan: invest it, move it to a holding company, or draw it"],
        ["Your lawyer and other advisors", "Never speaks to them", "Coordinates when structure, shares or the estate are involved"],
        ["The next ten years", "Not their department", "Part of the first conversation"]])
    who = (f'<div class="who"><div><p>{escape(BRAND)} is run by {escape(OPERATOR)}, an independent, Alberta-licensed '
           'life and living-benefits insurance broker who works with incorporated professionals and owner-managers.</p>'
           '<p>It isn’t an accounting firm. It exists because good accountants for incorporated owners are hard to find, '
           'and an introduction from someone who knows both sides saves a lot of trial and error.</p>'
           '<p>If you’d like to hear about corporate insurance as well, the form has a separate, optional box for that. '
           'Your introduction doesn’t depend on it.</p><p><a href="/how-it-works/">More on how it works and how we’re paid</a></p></div>'
           f'{headshot_html()}</div>')
    how = '<div class="cols3 runin">' + "".join(f'<div><p><em>{a}</em> {b}</p></div>' for a, b in [
        ("First,", "you fill in a short form about your business and what you need. Two minutes; no documents."),
        ("Then", f"{escape(OPERATOR)} reads it, may ask a question or two, and suggests an accountant by name, with the reason."),
        ("If you agree,", "you’re introduced by email. From there it’s between you and the firm. No obligation either way.")]) + "</div>"

    html = head(f"Find an Accountant for Your Calgary Business | {BRAND}",
                "Incorporated physicians, consultants and business owners in Calgary: get introduced to an accountant who plans, not just files. Free, consent-based introductions.",
                "/", [ld_faq(HOME_FAQS)])
    html += header("/") + f"""
<section class="hero"><div class="wrap hero-g"><div>
<p class="label">For incorporated professionals and owner-managers in Calgary</p>
<h1>Find the <span class="dbl-u">right</span> accountant for your Calgary business.</h1>
<p class="lead">Most incorporated owners don’t need a cheaper accountant. They need one who has seen their situation
many times before: a professional corporation, a salary-and-dividend decision, money piling up in the company.
Tell us where you are and we’ll introduce you to one.</p>
<p class="phero-cta"><a class="btn" href="{FORM}">Request an introduction</a><a class="textlink" href="/how-it-works/">How it works</a></p>
</div>
<aside class="asks" aria-label="Questions a good accountant asks"><p class="label">Questions a good accountant asks in the first meeting</p><ol>{asks_html}</ol></aside>
</div></section>
{sec(1, "Who it’s for", h2("Situations we introduce people for") + f'<ul class="toc">{toc}</ul>')}
{statement("Filing on time is the minimum. The useful part is everything that happens between filings.")}
{sec(2, "Filer or planner", h2("Two kinds of accountant") + compare)}
{sec(3, "How it works", h2("One form, one suggestion, your decision") + how)}
{sec(4, "Who runs this", h2("An insurance broker, not an accounting firm") + who)}
{sec(5, "Questions", qa(HOME_FAQS))}
{closer("Two minutes, no documents, and nothing shared without your say-so.")}""" + footer()
    write("/", html)


def build_form():
    path = FORM
    services = ["Year-end and corporate tax return (T2)", "Paying myself: salary, dividends or both",
                "What to do with cash in the corporation", "Incorporating or restructuring",
                "Setting up a holding company", "Estate or succession planning",
                "Switching from my current accountant", "Bookkeeping review or catch-up"]
    chk = "".join(f'<label><input type="checkbox" name="services" value="{escape(s)}"><span>{escape(s)}</span></label>' for s in services)
    def opts(xs, blank="Select"):
        return (f'<option value="">{blank}</option>' if blank else "") + "".join(f"<option>{escape(x)}</option>" for x in xs)
    html = head(f"Request an Introduction to a Calgary Accountant | {BRAND}",
                "Tell us about your corporation and what you need. We'll suggest a Calgary accountant who fits, and introduce you only if you agree.", path)
    html += header(path) + f"""
<section class="phero phero-form"><div class="wrap"><h1>Request an introduction</h1>
<p class="lead">A few questions about your business, so we can suggest the right accountant. About two minutes.</p></div></section>
<section class="formsec"><div class="wrap form-g">
<form id="leadform" method="post" action="/api/lead" novalidate>
<fieldset><legend><span class="n">01</span>You</legend>
<div class="two"><div class="field"><label for="name">Name <span class="req-mark" aria-hidden="true">*</span></label><input id="name" name="name" type="text" autocomplete="name" required maxlength="120"></div>
<div class="field"><label for="phone">Phone <span class="opt">optional</span></label><input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="40"></div></div>
<div class="field"><label for="email">Email <span class="req-mark" aria-hidden="true">*</span></label><input id="email" name="email" type="email" autocomplete="email" required maxlength="200"></div>
</fieldset>
<fieldset><legend><span class="n">02</span>Your business</legend>
<div class="two"><div class="field"><label for="business">What do you do? <span class="req-mark" aria-hidden="true">*</span></label><select id="business" name="business" required>{opts(["Physician or specialist", "Dentist or other health professional", "Consultant or contractor", "Engineer or technical professional", "Trades or construction", "Real estate or investments", "Other business"])}</select></div>
<div class="field"><label for="incorporated">Incorporated? <span class="req-mark" aria-hidden="true">*</span></label><select id="incorporated" name="incorporated" required>{opts(["Yes", "Yes, more than one company", "Not yet, thinking about it", "No"])}</select></div></div>
<div class="two"><div class="field"><label for="revenue">Annual revenue, roughly</label><select id="revenue" name="revenue">{opts(["Under $100K", "$100K to $250K", "$250K to $500K", "$500K to $1M", "Over $1M"], "Prefer not to say")}</select></div>
<div class="field"><label for="urgency">Timing</label><select id="urgency" name="urgency">{opts(["Just looking", "In the next month or two", "A deadline is coming up", "As soon as possible"], "")}</select></div></div>
</fieldset>
<fieldset><legend><span class="n">03</span>What you need</legend>
<p class="hint" id="svc-hint">Tick any that apply.</p><div class="checks" role="group" aria-describedby="svc-hint">{chk}</div>
<div class="field"><label for="message">Anything else? <span class="opt">optional</span></label><textarea id="message" name="message" rows="4" maxlength="2000" aria-describedby="msg-hint"></textarea>
<p class="hint" id="msg-hint">A sentence or two is plenty. Please don’t include SINs, account numbers or financial statements.</p></div>
</fieldset>
<div class="hp" aria-hidden="true"><label for="company_website">Leave this blank</label><input id="company_website" type="text" name="company_website" tabindex="-1" autocomplete="off"></div>
<input type="hidden" name="gclid" id="gclid"><input type="hidden" name="utm_source" id="utm_source"><input type="hidden" name="utm_medium" id="utm_medium"><input type="hidden" name="utm_campaign" id="utm_campaign"><input type="hidden" name="utm_term" id="utm_term"><input type="hidden" name="referrer" id="referrer">
<fieldset class="consent"><legend><span class="n">04</span>Consent</legend>
<label><input type="checkbox" name="consent_contact" value="yes" required><span>I agree that {escape(BRAND)} may contact me about this request, and may share my details with an accounting firm <strong>only after I’ve approved an introduction to that named firm</strong>. <span class="req-mark" aria-hidden="true">*</span></span></label>
<label><input type="checkbox" name="consent_insurance" value="yes"><span><em>Optional.</em> I’d also like to hear about corporate insurance or planning options from {escape(OPERATOR)}, a licensed insurance broker who runs this site. This is separate from my introduction and I can say no at any time.</span></label>
</fieldset>
<div class="submit-row"><button class="btn" type="submit" id="submitbtn">Send my request</button>
<p class="small"><span class="req-mark" aria-hidden="true">*</span> Required. See <a href="/privacy/">privacy and consent</a>.</p></div>
<div id="formmsg" role="alert" aria-live="assertive"></div>
</form>
<aside class="side"><p class="label">What happens next</p>
<ol class="side-steps"><li>We read your details, usually within one business day.</li>
<li>We may email or call with a question or two.</li><li>We suggest an accountant by name, and why.</li><li>You decide. If yes, we introduce you by email.</li></ol>
<p class="label">Not an accounting firm</p><p>We don’t prepare returns or give tax advice. The firm you’re introduced to does that, and sets its own fees.</p>
</aside>
</div></section>
<script src="/form.js" defer></script>""" + footer()
    write(path, html)


def build_thanks():
    conv = ""
    if GADS_ID and GADS_LEAD_LABEL:
        conv = f'<script>gtag("event","conversion",{{"send_to":"{GADS_LEAD_LABEL}"}});</script>'
    html = head(f"Request received | {BRAND}", "Your request has been received.", "/thank-you/", noindex=True)
    html += header("/thank-you/") + f"""<section class="phero"><div class="wrap narrow"><p class="label">Request received</p>
<h1>Thank you. We’ll be in touch.</h1>
<p class="lead">We usually reply within one business day, either with a question or with a suggested accountant and the reason
we think they fit. <strong>Nothing is shared with any accounting firm until you’ve approved the introduction.</strong></p>
<p>While you wait:</p>{dash(['<a href="/business-tax-planning-calgary/">Tax, estate and succession planning</a>',
                            '<a href="/change-accountants-calgary/">How changing accountants works</a>'])}</div></section>{conv}""" + footer()
    write("/thank-you/", html)


def build_how():
    path = "/how-it-works/"
    steps = numbered([
        ("You send the form", "Your business, whether it’s incorporated, and what you need help with. No documents."),
        (f"{escape(OPERATOR)} reads it", "Usually within one business day. You may get an email or a call with a question or two."),
        ("You get a suggestion", "An accountant by name, and why we think they fit. If we don’t know anyone suitable, we’ll say so."),
        ("You decide", "If you agree, we introduce you by email. If you don’t, nothing is shared and that’s the end of it."),
        ("You and the firm take it from there", "Scope, fees and the engagement are between you and them.")])
    html = head(f"How It Works | {BRAND}", "How our accountant introductions work, who runs the site, how we're paid, and what we don't do.", path,
                [ld_crumbs("How it works", path)])
    html += header(path) + page_hero("How it works", "How it works",
        f"{escape(BRAND)} introduces incorporated professionals and owner-managers in Calgary to accountants who suit their "
        "situation. Here is exactly what happens, who is behind it, and what it isn’t.")
    html += sec(1, "The process", h2("From form to introduction") + steps)
    html += sec(2, "What we don’t do", h2("The limits") + dash([
        "We’re not an accounting firm, a law firm or a tax advisor, and we don’t prepare returns.",
        "We don’t promise tax savings or outcomes, and we don’t set or collect accounting fees.",
        "We don’t share your details with anyone until you’ve agreed to a specific introduction.",
        "We don’t make the insurance conversation a condition of anything."]))
    html += sec(3, "Who runs this", h2(f"{escape(OPERATOR)}") +
        f'<div class="who"><div><p>{escape(OPERATOR_NOTE)}</p><p>Gavin works with incorporated professionals and '
        'owner-managers on corporate insurance and living-benefits planning. Those clients ask, often, whether he knows a '
        'good accountant. This site is the organised version of that answer.</p>'
        '<p>Because he is an insurance broker, you will always be told plainly when anything insurance-related is on offer. '
        'It’s optional and separate, and you can ignore it.</p></div>' + headshot_html() + "</div>")
    html += sec(4, "How we’re paid", h2("You don’t pay us") +
        "<p>There’s no fee to you for an introduction. Some accountants we introduce people to may also refer clients to "
        "Gavin’s insurance practice. If there is ever a financial arrangement with the firm we suggest, you’ll be told "
        "before you agree to the introduction.</p>")
    html += closer("When you’re ready, it takes about two minutes.") + footer()
    write(path, html)


def build_privacy():
    path = "/privacy/"
    contact = (f'<a href="mailto:{escape(CONTACT_EMAIL)}">{escape(CONTACT_EMAIL)}</a>' if CONTACT_EMAIL
               else "the email address in any message you receive from us")
    parts = [
        ("Who is responsible", f"<p>{escape(OPERATOR)} operates {escape(BRAND)} and is responsible for the personal information collected through it. Contact: {contact}.</p>"),
        ("What we collect", "<p>What you type into the form: name, email, phone (optional), business type, whether you’re incorporated, revenue band, timing, the services you tick and any message. We also record basic advertising information, such as the page that referred you and any campaign tags in the link you followed (for example a Google Ads click ID).</p>"),
        ("Why we collect it", "<p>To reply to your request, suggest a suitable accounting firm and, only after you approve an introduction to a named firm, share your details with that firm. Advertising information is used to understand which ads and pages work.</p>"),
        ("Who we share it with", "<p>Only the accounting firm you have approved, and only after you approve it. Our email and hosting providers process the information on our behalf to deliver the service. We don’t sell your information.</p>"),
        ("Optional insurance contact", f"<p>If you tick the optional box, {escape(OPERATOR)} may contact you about corporate insurance or planning. This consent is separate from your introduction, isn’t required for it, and can be withdrawn at any time.</p>"),
        ("What not to send", "<p>Please don’t send tax returns, social insurance numbers, bank or account details, or financial statements through the form or by reply.</p>"),
        ("How long we keep it", "<p>Only as long as needed for the purposes above. [Retention period to be confirmed before launch.]</p>"),
        ("Access, correction and withdrawal", f"<p>You can ask to see or correct the information we hold about you, withdraw consent, or ask us to delete it, by contacting {contact}.</p>"),
    ]
    body = "".join(f'<div class="pol"><h2>{h}</h2>{b}</div>' for h, b in parts)
    html = head(f"Privacy and Consent | {BRAND}", "How we collect, use and share your information, and the consent we ask for.", path)
    html += header(path) + page_hero("", "Privacy and consent",
        "What we collect through this site, why, and who sees it.")
    html += ('<section class="sec"><div class="wrap g"><div class="sec-label"><p class="draft">Draft for review against '
             'Alberta’s Personal Information Protection Act (PIPA) before launch.</p></div>'
             f'<div class="sec-body policy">{body}</div></div></section>') + footer()
    write(path, html)


def build_404():
    mail = f' or email <a href="mailto:{escape(CONTACT_EMAIL)}">{escape(CONTACT_EMAIL)}</a>' if CONTACT_EMAIL else ""
    html = head(f"Page not found | {BRAND}", "This page doesn't exist.", "/404/", noindex=True)
    html += header("") + f"""<section class="phero nf"><div class="wrap narrow"><p class="label">404</p>
<h1>That page isn’t on the books.</h1>
<p class="lead">The link may be old or mistyped. Try one of these{mail}.</p>
<ul class="toc">{"".join(f'<li><a href="{u}"><span class="t">{t}</span><span class="d">{d}</span></a></li>' for t, u, d in [
    ("Home", "/", "Start again from the top"),
    ("Request an introduction", FORM, "Two minutes, no documents"),
    ("Physicians", "/accountant-for-doctors-calgary/", "Accountants who work with professional corporations"),
    ("Consultants", "/accountant-for-consultants-calgary/", "Accountants for incorporated contractors")])}</ul>
</div></section>""" + footer()
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(html)


def build_extras():
    urls = ["/", FORM, "/how-it-works/", "/privacy/"] + [f"/{p['slug']}/" for p in PAGES]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"<url><loc>{DOMAIN}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write(sm)
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /thank-you/\nSitemap: {DOMAIN}/sitemap.xml\n")


if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(STATIC, OUT)
    build_home()
    for p in PAGES:
        build_service(p)
    build_form(); build_thanks(); build_how(); build_privacy(); build_404(); build_extras()
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print(f"built {n} files into {OUT}/")
