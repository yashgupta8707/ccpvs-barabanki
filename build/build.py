#!/usr/bin/env python3
"""Static site builder for City College of Para-Veterinary Sciences.

Each file in build/pages/ starts with a front-matter block:
    ---
    title: Page title
    description: Meta description
    active: home
    ---
followed by the page body HTML. {{icon:name}} placeholders are replaced with
inline SVG icons. Output is written to site/<page>.html.

Run:  python3 build/build.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT.parent / "site"

ICONS = {
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "arrow": '<path d="M5 12h14M13 5l7 7-7 7"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "flask": '<path d="M9 3h6M10 3v6.5L4.5 19a1.5 1.5 0 0 0 1.3 2h12.4a1.5 1.5 0 0 0 1.3-2L14 9.5V3"/><path d="M7 15h10"/>',
    "microscope": '<path d="M6 18h8M3 22h18M14 22a7 7 0 1 0 0-14h-1"/><path d="M9 14h2M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2zM12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"/>',
    "stethoscope": '<path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6 6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6 6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "home": '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "heart": '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z"/><path d="M3.2 12h4.3l1.5-3 3 6 1.5-3h7.3"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "monitor": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "wifi": '<path d="M5 12.6a10 10 0 0 1 14 0M8.5 16.1a5 5 0 0 1 7 0M2 8.8a15 15 0 0 1 20 0M12 20h.01"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/><path d="M2 21c0-3 1.9-5.4 5.1-6 2.4-.5 4.9-2 5.9-3.5"/>',
    "truck": '<path d="M10 17h4V5H2v12h3M14 17h1M19 17h3v-3.3a1 1 0 0 0-.2-.6l-3.5-4.4A1 1 0 0 0 17.5 8H14"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "syringe": '<path d="m18 2 4 4M17 7l3-3M19 9 8.7 19.3a1 1 0 0 1-1.4 0l-2.6-2.6a1 1 0 0 1 0-1.4L15 5M9 11l4 4M5 19l-3 3M14 4l6 6"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.5 12.9 17 22l-5-3-5 3 1.5-9.1"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    "check": '<path d="M5 12l5 5L20 7"/>',
    "utensils": '<path d="M3 2v7c0 1.1.9 2 2 2h2a2 2 0 0 0 2-2V2M6 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/>',
    "snow": '<path d="M12 2v20M17 5l-5 5-5-5M17 19l-5-5-5 5M2 12h20M5 7l5 5-5 5M19 7l-5 5 5 5"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "map": '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
    "whatsapp": None,  # filled glyph, handled separately
}

WHATSAPP = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.2-.3-.3-.6-.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 0 1 2.2 12C2.2 6.6 6.6 2.2 12 2.2c2.6 0 5.1 1 6.9 2.9a9.7 9.7 0 0 1 2.9 6.9c0 5.4-4.4 9.8-9.8 9.8zm8.4-18.2A11.8 11.8 0 0 0 12 0C5.5 0 .2 5.3.2 11.9c0 2.1.5 4.1 1.6 5.9L0 24l6.3-1.7c1.7.9 3.7 1.4 5.7 1.4 6.5 0 11.9-5.3 11.9-11.9 0-3.2-1.2-6.2-3.5-8.4z"/></svg>')


def icon(name):
    if name == "whatsapp":
        return WHATSAPP
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONS[name] + "</svg>")


NAV = [
    ("home", "index.html", "Home"),
    ("about", "about.html", "About"),
    ("courses", "courses.html", "Courses"),
    ("facilities", "facilities.html", "Facilities"),
    ("admissions", "admissions.html", "Admissions"),
    ("gallery", "gallery.html", "Gallery"),
    ("administration", "administration.html", "Administration"),
    ("contact", "contact.html", "Contact"),
]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="assets/img/campus.jpg">
<meta name="theme-color" content="#0d3560">
<link rel="icon" href="assets/img/logo-mark.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
"""

HEADER = """<div class="topbar">
  <div class="container">
    <div class="topbar-info">
      <a href="tel:+918177001081">{{icon:phone}} +91 81770 01081</a>
      <a href="mailto:rajendraprasadeducationsociety@gmail.com" class="hide-sm">{{icon:mail}} rajendraprasadeducationsociety@gmail.com</a>
      <span class="hide-sm">{{icon:clock}} Mon – Sat: 9:00 AM – 5:00 PM</span>
    </div>
    <a href="admissions.html" class="topbar-badge">Admissions Open 2026–27</a>
  </div>
</div>
<header class="site-header">
  <div class="container">
    <a href="index.html" class="brand" aria-label="City College of Para-Veterinary Sciences — Home">
      <img src="assets/img/logo-mark.svg" alt="" width="50" height="46">
      <span class="brand-text">
        <small>City College of</small>
        <strong>Para-Veterinary Sciences</strong>
        <span class="loc">Pratapganj, Barabanki</span>
      </span>
    </a>
    <button class="nav-toggle" aria-label="Open menu" aria-expanded="false">{{icon:menu}}</button>
    <nav class="nav" aria-label="Main">
{nav}
      <a href="admissions.html#apply" class="btn btn-primary">Apply Now</a>
    </nav>
    <div class="nav-backdrop"></div>
  </div>
</header>
<main>
"""

FOOTER = """</main>
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="footer-brand">
          <span class="mark"><img src="assets/img/logo-mark.svg" alt=""></span>
          <strong>City College of<br>Para-Veterinary Sciences</strong>
        </div>
        <p>A centre for practical, skill-based education in veterinary pharmacy and livestock extension — preparing trained para-veterinary professionals for rural India.</p>
        <p style="margin:0;font-size:.88rem">A unit of Rajendra Prasad Education Society</p>
      </div>
      <div>
        <h4>Quick Links</h4>
        <ul>
          <li><a href="about.html">About the College</a></li>
          <li><a href="courses.html">Courses Offered</a></li>
          <li><a href="facilities.html">Campus &amp; Facilities</a></li>
          <li><a href="admissions.html">Admissions</a></li>
          <li><a href="gallery.html">Gallery</a></li>
          <li><a href="administration.html">Administration</a></li>
        </ul>
      </div>
      <div>
        <h4>Programmes</h4>
        <ul>
          <li><a href="courses.html#dvp">Diploma in Veterinary Pharmacy</a></li>
          <li><a href="courses.html#dle">Livestock Extension Programme</a></li>
          <li><a href="facilities.html#ai">AI &amp; Livestock Training</a></li>
          <li><a href="facilities.html#clinic">Clinical Training Centre</a></li>
          <li><a href="admissions.html#faq">Admission FAQs</a></li>
        </ul>
      </div>
      <div>
        <h4>Get in Touch</h4>
        <ul class="footer-contact">
          <li>{{icon:pin}}<span>Lakshbar Bajha, Pratapganj,<br>Barabanki, Uttar Pradesh</span></li>
          <li>{{icon:phone}}<a href="tel:+918177001081">+91 81770 01081</a></li>
          <li>{{icon:mail}}<a href="mailto:rajendraprasadeducationsociety@gmail.com" style="word-break:break-all">rajendraprasadeducationsociety@gmail.com</a></li>
          <li>{{icon:clock}}<span>Mon – Sat: 9:00 AM – 5:00 PM</span></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container">
      <span>&copy; <span id="year">2026</span> City College of Para-Veterinary Sciences, Barabanki. All rights reserved.</span>
      <span>Manager: Mr. Amrit Srivastava</span>
    </div>
  </div>
</footer>
<a class="float-call" href="https://wa.me/918177001081" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{{icon:whatsapp}}</a>
<script src="assets/js/main.js"></script>
</body>
</html>
"""


def render_icons(html):
    return re.sub(r"\{\{icon:([a-z]+)\}\}", lambda m: icon(m.group(1)), html)


def build_page(src):
    text = src.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines())
    body = text[m.end():]
    active_attr = ' class="active" aria-current="page"'
    nav = "\n".join(
        '      <a href="%s"%s>%s</a>' % (href, active_attr if key == meta["active"] else "", label)
        for key, href, label in NAV
    )
    html = (HEAD.format(title=meta["title"], description=meta["description"])
            + HEADER.replace("{nav}", nav) + body + FOOTER)
    out = SITE / (src.stem + ".html")
    out.write_text(render_icons(html), encoding="utf-8")
    print("built", out.relative_to(SITE.parent))


if __name__ == "__main__":
    for page in sorted((ROOT / "pages").glob("*.html")):
        build_page(page)
