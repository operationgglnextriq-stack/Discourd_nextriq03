"""
NEXTRIQ Discord v3.0 — Complete Server Setup
=============================================
Verbeterde structuur met:
- Ink Approved afdeling (eigen setters)
- NEXTRIQ Label / Platform afdeling (eigen setters)  
- Outreach afdeling (cold outreachers)
- Content & Marketing (creators + ambassadeurs samen, duidelijk gesplitst)
- Marketing Middelen prominente eigen plek
- Tech & Oplevering samengevoegd
- Franchise Boris kanaal
- Platform strategie kanaal
"""

import requests, os, time, sys

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SERVER_ID  = os.environ.get("SERVER_ID")
BASE       = "https://discord.com/api/v10"
HEADERS    = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}

# ─── API ──────────────────────────────────────────────────────────────────────

def api(method, endpoint, payload=None, retries=5):
    url = f"{BASE}{endpoint}"
    for attempt in range(retries):
        r = getattr(requests, method)(url, headers=HEADERS, json=payload)
        if r.status_code == 429:
            wait = r.json().get("retry_after", 2)
            print(f"  ⏳ Rate limit — wacht {wait}s...")
            time.sleep(float(wait) + 0.5)
            continue
        if r.status_code in (200, 201):
            return r.json()
        print(f"  ⚠️  {method.upper()} {endpoint} → {r.status_code}: {r.text[:200]}")
        return None
    return None

# ─── RECHTEN ──────────────────────────────────────────────────────────────────

VIEW      = 1024
SEND      = 2048
HIST      = 65536
REACT     = 64
ATTACH    = 32768
EMBED     = 16384
CONN      = 1048576
SPEAK     = 2097152
MGMSG     = 8192
ALL_TEXT  = VIEW | SEND | HIST | REACT | ATTACH | EMBED
READ_ONLY = VIEW | HIST | REACT

def allow(rid, p):    return {"id": rid, "type": 0, "allow": str(p), "deny": "0"}
def deny(rid, p=VIEW): return {"id": rid, "type": 0, "allow": "0", "deny": str(p)}
def ev_allow(ev):     return {"id": ev, "type": 0, "allow": str(ALL_TEXT), "deny": "0"}
def ev_deny(ev):      return {"id": ev, "type": 0, "allow": "0", "deny": str(VIEW)}

def create_role(name, color_hex, hoist=True, mentionable=True):
    res = api("post", f"/guilds/{SERVER_ID}/roles", {
        "name": name, "color": int(color_hex, 16),
        "hoist": hoist, "mentionable": mentionable
    })
    time.sleep(0.5)
    if res:
        print(f"  ✅ Rol: {name}")
        return res["id"]
    return None

def create_cat(name, pos, overwrites):
    res = api("post", f"/guilds/{SERVER_ID}/channels", {
        "name": name, "type": 4, "position": pos,
        "permission_overwrites": overwrites
    })
    time.sleep(0.5)
    if res:
        print(f"\n📁 {name}")
        return res["id"]
    return None

def ch(name, cat, topic, overwrites, ro=False):
    res = api("post", f"/guilds/{SERVER_ID}/channels", {
        "name": name, "type": 0, "parent_id": cat,
        "topic": topic, "permission_overwrites": overwrites
    })
    time.sleep(0.5)
    if res:
        print(f"  {'🔒' if ro else '  '} #{name}")
        return res["id"]
    return None

def vc(name, cat, overwrites):
    res = api("post", f"/guilds/{SERVER_ID}/channels", {
        "name": name, "type": 2, "parent_id": cat,
        "permission_overwrites": overwrites
    })
    time.sleep(0.5)
    if res:
        print(f"    🔊 {name}")

def pin(channel_id, content):
    msg = api("post", f"/channels/{channel_id}/messages", {"content": content})
    if msg:
        time.sleep(0.3)
        api("put", f"/channels/{channel_id}/pins/{msg['id']}")
        time.sleep(0.3)

def delete_all():
    channels = api("get", f"/guilds/{SERVER_ID}/channels")
    if channels:
        for c in channels:
            api("delete", f"/channels/{c['id']}")
            time.sleep(0.3)

# ═══════════════════════════════════════════════════════════════════════════════
def main():
    if not BOT_TOKEN or not SERVER_ID:
        print("❌ BOT_TOKEN of SERVER_ID ontbreekt")
        sys.exit(1)

    guild = api("get", f"/guilds/{SERVER_ID}")
    if not guild:
        print("❌ Server niet gevonden")
        sys.exit(1)

    ev = SERVER_ID
    print(f"\n🚀 NEXTRIQ Discord v3.0 — {guild['name']}\n")

    print("🧹 Opruimen...")
    delete_all()

    # ═══════════════════════════════════
    # ROLLEN
    # ═══════════════════════════════════
    print("\n🎭 ROLLEN AANMAKEN...")
    r = {}
    r["founder"]      = create_role("🚀 Founder",             "E67E22")
    r["headtech"]      = create_role("⚡ Head of Tech",           "27AE60")
    r["webdev"]       = create_role("💻 Head of Web Dev",      "1ABC9C")
    r["manager"]      = create_role("🛡️ Sales Manager",       "8E44AD")
    r["top_setter"]   = create_role("🏆 Top Setter",           "F1C40F")
    r["setter"]       = create_role("🎯 Setter",               "2980B9")
    r["new_setter"]   = create_role("🆕 Nieuwe Setter",        "95A5A6")
    r["ink_setter"]   = create_role("🖤 Ink Setter",           "2C2C2C")  # Ink Approved setters
    r["platform_set"] = create_role("🌐 Platform Setter",      "16A085")  # Vergelijkingssite setters
    r["outreacher"]   = create_role("📧 Outreacher",           "E74C3C")  # Cold outreachers
    r["closer"]       = create_role("🎯 Closer",               "C0392B")
    r["creator"]      = create_role("🎬 Creator",              "E91E8C")
    r["ambassador"]   = create_role("🌟 Ambassadeur",          "52BE80")
    r["bot"]          = create_role("🤖 NEXTRIQ Bot",          "5865F2", hoist=False)

    fo  = r["founder"]
    cf  = r["headtech"]
    mgr = r["manager"]
    wd  = cf  # Head of Tech = Head of Tech — zelfde niveau
    ts  = r["top_setter"]
    s   = r["setter"]
    ns  = r["new_setter"]
    ink = r["ink_setter"]
    ps  = r["platform_set"]
    out = r["outreacher"]
    cl  = r["closer"]
    cr  = r["creator"]
    amb = r["ambassador"]

    # Groepen
    mgmt        = [fo, cf, mgr, wd]
    leaders     = [fo, cf, mgr, wd]
    all_setters = [fo, mgr, ts, s, ns, out, ink, ps]
    all_sales   = [fo, cf, mgr, ts, s, ns, cl, out, ink, ps]
    intern_all  = [fo, cf, mgr, wd, ts, s, ns, cl, cr, out, ink, ps]
    tech_team   = [fo, cf, mgr, wd]
    content_cr  = [fo, mgr, cr]
    content_all = [fo, mgr, cr, amb]
    ink_team    = [fo, mgr, ink]
    plat_team   = [fo, mgr, ps]
    out_team    = [fo, mgr, out]

    print("\n📋 KANALEN AANMAKEN...")

    # ════════════════════════════════════════
    # 1. INFORMATIE
    # ════════════════════════════════════════
    cat = create_cat("📌 INFORMATIE", 0, [ev_allow(ev)])

    welkom_id = ch("welkom-en-regels", cat,
        "Welkomsttekst, serverregels, roluitleg en CRM-link. Altijd lezen bij onboarding.",
        [ev_allow(ev), deny(ev, SEND)], ro=True)

    ch("aankondigingen", cat,
        "Officiële berichten van Founder en Manager. Zet notificaties aan voor dit kanaal.",
        [ev_allow(ev), deny(ev, SEND),
         allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)], ro=True)

    ch("product-updates", cat,
        "Actuele producten en prijzen. Altijd checken voor een klantgesprek.",
        [ev_allow(ev), deny(ev, SEND),
         allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)], ro=True)

    ch("systeem-updates", cat,
        "Updates over CRM (crmoas.vercel.app), Discord, Zapier en tools.",
        [ev_allow(ev), deny(ev, SEND),
         allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)], ro=True)

    # ════════════════════════════════════════
    # 2. TEAM
    # ════════════════════════════════════════
    cat = create_cat("💬 TEAM", 1,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ch("team-chat", cat, "Algemeen teamkanaal voor iedereen.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ch("beschikbaarheid", cat,
        "Dagelijks vóór 9:30 doorgeven. ✅ BESCHIKBAAR [uren] [focus] of ❌ NIET BESCHIKBAAR [reden].",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ch("vragen-aan-manager", cat,
        "Alle vragen aan Kim komen HIER. Nooit in DM. Kim reageert binnen 4 uur op werkdagen.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ch("wins-van-de-dag", cat,
        "Vier elke win — groot of klein. Deal, activatie, positieve reactie. Minimaal één per dag!",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    # ════════════════════════════════════════
    # 3. KENNIS & SCRIPTS
    # ════════════════════════════════════════
    cat = create_cat("🧠 KENNIS & SCRIPTS", 2,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ro_intern = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in intern_all] + \
                [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG)]

    ch("kennis-en-sales-scripts", cat,
        "Alle verkoopscripts per product + BANT+ protocol. Verplicht lezen voor elk gesprek.",
        ro_intern, ro=True)

    ch("bezwaren-behandeling", cat,
        "Hoe om te gaan met elk bezwaar per producttype. Te duur? Geen tijd? Hier staat het antwoord.",
        ro_intern, ro=True)

    ch("cta-bibliotheek", cat,
        "Alle goedgekeurde calls-to-action per product. Gebruik ALLEEN goedgekeurde CTAs.",
        ro_intern, ro=True)

    ch("handboeken", cat,
        "Links naar alle handboeken: Setter, Closer, Creator, Ambassadeur, Manager + CRM handleiding.",
        ro_intern, ro=True)

    # ════════════════════════════════════════
    # 4. MARKETING MIDDELEN  ← EIGEN PROMINENTE CATEGORIE
    # ════════════════════════════════════════
    cat = create_cat("🎨 MARKETING MIDDELEN", 3,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ro_mkt = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in intern_all] + \
             [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG), allow(cr, ALL_TEXT)]

    ch("canva-templates", cat,
        "Alle goedgekeurde Canva-templates. Stories, Reels, carrousels, visitekaartjes. Gebruik alleen deze.",
        ro_mkt, ro=True)

    ch("goedgekeurde-links", cat,
        "Goedgekeurde Instagram/TikTok/LinkedIn links voor setters om te delen met prospects.",
        ro_mkt, ro=True)

    ch("brand-assets", cat,
        "Logo's, kleuren (#1B2A4A navy, #6B3FA0 paars), fonts, huisstijlgids. Officiële NEXTRIQ branding.",
        ro_mkt, ro=True)

    ch("campagne-updates", cat,
        "Actieve campagnes en wekelijkse CTA-instructies. Welk product staat centraal? Check dit elke maandag.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_all + [mgr, s, ts]])

    ch("content-ideeen", cat,
        "Deel content-ideeën voor NEXTRIQ. Format: Platform | Idee | Doelgroep | Verwacht bereik.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    # ════════════════════════════════════════
    # 5. SALES — NEXTRIQ CORE
    # ════════════════════════════════════════
    cat = create_cat("📊 SALES & RESULTATEN", 4,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    ch("crm-updates", cat,
        "⚡ ZAPIER — Automatisch: nieuwe lead in CRM. Niet handmatig posten.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    dagrapport_id = ch("dagrapport", cat,
        "Verplicht vóór 18:00 elke werkdag. Format vastgepind. Geen rapport = niet geteld.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    ch("leaderboard", cat,
        "⚡ ZAPIER — Elke vrijdag 16:00 automatisch: top 3 setters van de week.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in all_sales] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    ch("booked-calls", cat,
        "⚡ ZAPIER — Automatisch: Calendly-afspraak ingepland. Closers: check dit elk uur.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    ch("deals-gesloten", cat,
        "🔥 ⚡ ZAPIER — Deal gesloten. Reageer! Een team dat viert groeit.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    ch("betalingen-ontvangen", cat,
        "💰 ⚡ ZAPIER — Betaling ontvangen → commissie-teller loopt. Alleen management post handmatig.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in all_sales] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    ch("no-shows", cat,
        "Closer meldt no-show direct na gemiste afspraak. Format: Closer | Klant | Tijd | Reden | Actie.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    # ════════════════════════════════════════
    # 6. OUTREACH ← NIEUW
    # ════════════════════════════════════════
    cat = create_cat("📧 OUTREACH", 5,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in out_team + [ts, s]])

    ro_out = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in out_team] + \
             [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG)]

    ch("outreach-scripts", cat,
        "Cold call scripts, email templates, LinkedIn-berichten. Alleen goedgekeurde scripts gebruiken.",
        ro_out, ro=True)

    ch("mijn-contacten", cat,
        "Outreacher logt elk nieuw contact. Format: Bedrijf | Contact | Methode | Status | Volgende actie.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in out_team])

    ch("leads-doorgestuurd", cat,
        "Als outreacher een contact omzet naar lead voor setter. Format: Bedrijf | Contact | Waarom doorgestuurd.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in out_team + [s, ts]])

    ch("dagrapport-outreach", cat,
        "Dagrapport voor outreachers. Vóór 18:00. Format: Contacten benaderd | Reacties | Leads doorgezet | Pijnpunten.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in out_team])

    ch("resultaten-outreach", cat,
        "⚡ ZAPIER — Wekelijks automatisch overzicht: contacten, conversie, top outreacher.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in out_team] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    # ════════════════════════════════════════
    # 7. INK APPROVED ← NIEUW
    # ════════════════════════════════════════
    cat = create_cat("🖤 INK APPROVED", 6,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team])

    ro_ink = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in ink_team] + \
             [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG)]

    ch("ink-info-en-scripts", cat,
        "Productinfo Ink Approved + scripts voor tatu-shops. Gratis (≤5) → €29/mnd upgrade.",
        ro_ink, ro=True)

    ch("ink-leads", cat,
        "Nieuwe tatu-shop leads loggen. Format: Shopnaam | Stad | Contact | Status | Setter.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team])

    ch("ink-upgrades", cat,
        "⚡ ZAPIER — Automatisch: upgrade naar €29/mnd. Elke upgrade telt als recurring MRR.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in ink_team] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    ch("ink-dagrapport", cat,
        "Dagrapport Ink Approved setters. Format: Shops benaderd | Reacties | Upgrades | Pijnpunten.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team])

    ch("ink-klanten-actief", cat,
        "Overzicht alle actieve Ink Approved abonnementen. Kim bijwerkt bij elke upgrade/opzegging.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team])

    ch("ink-feedback", cat,
        "Klantfeedback en verbeterpunten voor Erik. 3+ dezelfde klacht = prioriteit voor product update.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team + [cf]])

    # ════════════════════════════════════════
    # 8. NEXTRIQ LABEL / PLATFORM ← NIEUW
    # ════════════════════════════════════════
    cat = create_cat("🌐 NEXTRIQ LABEL & PLATFORM", 7,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team])

    ro_plat = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in plat_team] + \
              [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG)]

    ch("platform-info-en-doelen", cat,
        "Wat is het platform, wie benaderen we, targets en pitch. Verplicht lezen voor start.",
        ro_plat, ro=True)

    ch("pitch-en-scripts", cat,
        "Scripts voor aanbieders benaderen. Pitch: gratis listing → betaald pakket → NEXTRIQ Label.",
        ro_plat, ro=True)

    ch("aanbieders-prospectie", cat,
        "Welke AI-bureaus/SaaS/consultants gaan we benaderen? Planning en taakverdeling per setter.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team])

    ch("aanbieders-pipeline", cat,
        "Status per aanbieder. Format: Aanbieder | Contact | Status (gratis/€99/€299/Label) | Setter | Datum.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team])

    ch("platform-deals", cat,
        "⚡ ZAPIER — Nieuwe betalende aanbieder op het platform. Elke betaling = recurring MRR.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in plat_team] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    ch("label-certificeringen", cat,
        "Aanbieders die NEXTRIQ Label hebben aangevraagd. Head of Tech + Saif keuren goed. Status bijhouden.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team + [cf]])

    ch("platform-dagrapport", cat,
        "Dagrapport platform setters. Format: Aanbieders benaderd | Reacties | Nieuwe listings | Upgrades.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team])

    ch("platform-bouwen", cat,
        "Head of Tech post updates over de platformbouw. Features live, bugs, roadmap wijzigingen.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team + [cf]])

    # ════════════════════════════════════════
    # 9. CONTENT & CREATORS + AMBASSADEURS SAMEN
    # ════════════════════════════════════════
    cat = create_cat("🎬 CONTENT & CREATORS", 8,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_all + [mgr]])

    # --- Creators sectie ---
    ro_cr = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in content_all + [mgr]] + \
            [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)]

    ch("content-briefings", cat,
        "Wekelijkse briefings van Founder — elke maandag. Alleen Founder post. Dit is jouw taak voor de week.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in content_all + [mgr]] +
        [allow(fo, ALL_TEXT|MGMSG)], ro=True)

    ch("content-planning", cat,
        "Weekplanning per creator. Wat maak je, wanneer gaat het live, welk product promoot je?",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_cr + [mgr]])

    ch("content-geplaatst", cat,
        "Screenshot + link zodra content live gaat. Format: Platform | Type | CTA | Link | Creator.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_all + [mgr]])

    ch("dm-opvolging", cat,
        "Creator meldt inkomende DMs voor setter. Format: Platform | Van wie | Inhoud | Urgentie.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_cr + [s, ts, mgr]])

    # --- Ambassadeurs sectie (in zelfde categorie maar eigen kanalen) ---
    ch("amb-briefings-en-regels", cat,
        "Onboarding info + handboek link + campagne-instructies voor ambassadeurs. Lees dit eerst.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in content_all + [mgr]] +
        [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)], ro=True)

    ch("amb-chat", cat,
        "Onderling overleg voor ambassadeurs. Vragen, samenwerking, content-ideeën delen.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr, amb]])

    ch("amb-wins-en-resultaten", cat,
        "Vier je successen als ambassadeur! Leads via jouw kanaal, virale content, positieve reacties.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr, amb, cr]])

    ch("commissie-vragen", cat,
        "Vragen over commissieberekening of uitbetaling. Kim antwoordt binnen 2 werkdagen. Deadline rekening: 5e vd maand.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr, amb, cr]])

    ch("leaderboard-amb", cat,
        "⚡ ZAPIER — Maandelijks automatisch: top ambassadeurs op basis van omzet via hun kanaal.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in [fo, mgr, amb, cr]])

    # ════════════════════════════════════════
    # 10. TECH & OPLEVERING (samengevoegd)
    # ════════════════════════════════════════
    cat = create_cat("⚙️ TECH & OPLEVERING", 9,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    ch("tech-vragen", cat,
        "Technische vragen voor Erik. Altijd hier, nooit in DM. Erik reageert binnen 1 werkdag.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ch("ai-agents", cat,
        "Updates over actieve AI agents in ontwikkeling. Versies, statuswijzigingen, livegang.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team])

    ch("automatiseringen", cat,
        "Documentatie alle Zapier/Make automatiseringen. Format: Naam | Trigger | Actie | Status.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team])

    ch("tech-demo-aanvragen", cat,
        "⚡ ZAPIER — AI Intelligence Scan aangevraagd. Erik en Founder handelen af.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team])

    ch("demo-aanvragen", cat,
        "⚡ ZAPIER — Website demo aangevraagd. Webdeveloper pakt dit op binnen 24 uur.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    ch("klant-onboarding", cat,
        "Na deal: closer stuurt klantinfo + briefing naar webdeveloper. Format vastgepind.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    ch("projecten-lopend", cat,
        "Overzicht actieve webprojecten. Webdeveloper bijwerkt wekelijks status.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    ch("opleveringen", cat,
        "Project afgerond. Na oplevering: upsell hosting €50/mnd aanbieden. Format: Klant | Project | Datum.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    # ════════════════════════════════════════
    # 11. ESCALATIE
    # ════════════════════════════════════════
    cat = create_cat("🚨 ESCALATIE", 10,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    for kanaal, topic in [
        ("maatwerk-goedkeuring",
         "Afwijkende prijs of scope. Closer vraagt aan — Founder keurt goed/af. NOOIT korting zonder goedkeuring hier."),
        ("betalingsproblemen",
         "Betalingsissues, chargebacks, openstaande facturen. Vertrouwelijk."),
        ("klachten-en-conflicten",
         "Klantklachten of interne conflicten. Strikt vertrouwelijk."),
        ("setter-problemen",
         "Kim rapporteert setterissues aan Saif. CRM-fouten, naleving, prestaties."),
    ]:
        ch(kanaal, cat, topic,
           [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    # Extra escalatie kanalen voor nieuwe afdelingen
    ch("ink-problemen", cat,
        "Issues met Ink Approved setters of klanten. Kim rapporteert aan Saif.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr]])

    ch("platform-problemen", cat,
        "Issues met platform setters of aanbieders. Kim rapporteert aan Saif en de Head of Tech.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    # ════════════════════════════════════════
    # 12. MANAGEMENT
    # ════════════════════════════════════════
    cat = create_cat("🗂️ MANAGEMENT", 11,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    ch("manager-saif", cat,
        "Directe lijn Kim ↔ Saif. Strategische updates, beslissingen, vertrouwelijk.",
        [ev_deny(ev), allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    ch("commissie-verwerking", cat,
        "Maandelijks commissieoverzicht. Vóór de 5e van elke maand. Kim indienen — Saif goedkeuren.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr]])

    ch("marktdata-analyse", cat,
        "Wekelijkse samenvatting pijnpunten van setters en outreachers. 3+ hetzelfde = potentieel nieuw product.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    ch("franchise-boris", cat,
        "Boris (NEXTRIQ Oekraïne) maandrapport + 20% royalty + strategische afstemming. Alleen Saif ↔ Boris.",
        [ev_deny(ev), allow(fo, ALL_TEXT)])

    ch("platform-strategie", cat,
        "NEXTRIQ Label / vergelijkingssite strategie en beslissingen. Saif × Head of Tech.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf]])

    ch("team-beschikbaarheid", cat,
        "Overzicht team planning, verlof en afwezigheid. Kim beheert voor rapportage aan Saif.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr]])

    # ════════════════════════════════════════
    # 13. VOICE KANALEN
    # ════════════════════════════════════════
    cat = create_cat("🔊 VOICE", 12,
        [ev_deny(ev)] + [allow(x, ALL_TEXT|CONN|SPEAK) for x in intern_all])

    voice_channels = [
        ("🔊 Algemeen",                intern_all),
        ("📅 Wekelijkse Teammeeting",  intern_all),
        ("🎯 Setter Room",             [fo, mgr, ts, s, ns]),
        ("📧 Outreach Room",           [fo, mgr, out]),
        ("🖤 Ink Approved Room",       [fo, mgr, ink]),
        ("🌐 Platform Room",           [fo, cf, mgr, ps]),
        ("🎯 Closer Room",             [fo, mgr, cl]),
        ("🎬 Creator Room",            [fo, mgr, cr, amb]),
        ("⚙️ Tech Room",           [fo, cf, mgr, wd]),
        ("📍 1-op-1 met Kim",         [fo, mgr]),
    ]

    for vname, allowed in voice_channels:
        api("post", f"/guilds/{SERVER_ID}/channels", {
            "name": vname, "type": 2, "parent_id": cat,
            "permission_overwrites":
                [ev_deny(ev)] + [allow(x, CONN|SPEAK|VIEW) for x in allowed]
        })
        time.sleep(0.5)
        print(f"    🔊 {vname}")

    # ════════════════════════════════════════
    # WELKOMSTBERICHT VASTPINNEN
    # ════════════════════════════════════════
    if welkom_id:
        print("\n📌 Welkomstbericht vastpinnen...")
        welkom = """# 🚀 Welkom bij NEXTRIQ!

**NEXTRIQ | Business Intelligence voor het Nederlandse bedrijfsleven**

---

## 🗺️ Serverstructuur

**📌 INFORMATIE** — Lees dit eerst. Altijd actueel houden.
**💬 TEAM** — Dagelijkse communicatie, beschikbaarheid, wins.
**🧠 KENNIS & SCRIPTS** — Sales scripts, bezwaren, handboeken. Lees vóór elk gesprek.
**🎨 MARKETING MIDDELEN** — Templates, links, brand assets, campagnes.
**📊 SALES & RESULTATEN** — CRM updates, dagrapport, leaderboard, deals.
**📧 OUTREACH** — Cold outreach afdeling. Eigen scripts en rapportage.
**🖤 INK APPROVED** — Tatu-shop product. Eigen setters, eigen pipeline.
**🌐 NEXTRIQ LABEL & PLATFORM** — Vergelijkingssite. Eigen setters, aanbieders werven.
**🎬 CONTENT & CREATORS** — Briefings, planning, creators + ambassadeurs.
**⚙️ TECH & OPLEVERING** — Webprojecten, AI-agents, tech-vragen.
**🚨 ESCALATIE** — Alleen Founder + Manager. Uitzonderingen en problemen.
**🗂️ MANAGEMENT** — Intern management. Alleen Founder + Manager.

---

## 📋 De 7 regels van NEXTRIQ

**Regel 1** — Elke lead in het CRM. Ook afwijzingen. Altijd.
**Regel 2** — Pijnpunt Marktdata invullen bij elke interactie. Zelfs bij nee.
**Regel 3** — Dagrapport vóór 18:00 elke werkdag.
**Regel 4** — Nooit korting zonder goedkeuring in #maatwerk-goedkeuring.
**Regel 5** — AI Agency altijd pas na AI Intelligence Scan.
**Regel 6** — DMs binnen 2 uur beantwoorden.
**Regel 7** — Vragen aan manager? #vragen-aan-manager. Nooit in DM.

---

## 💻 Systemen

**CRM:** crmoas.vercel.app
**Calendly:** [invullen]
**Google Drive (handboeken):** [invullen]

---

*NEXTRIQ v3.0 — Gebouwd voor groei. Aangedreven door data.*

> 💡 Head of Web Dev wordt tijdelijk gedragen door Saif (Founder) totdat er een nieuwe webdeveloper is aangesteld."""
        pin(welkom_id, welkom)
        print("  ✅ Welkomstbericht vastgepind!")

    if dagrapport_id:
        print("\n📌 Dagrapport format vastpinnen...")
        dagrapport_format = """📋 **DAGRAPPORT FORMAT — kopieer en vul in**

```
📋 DAGRAPPORT [datum] — [jouw naam]

Leads benaderd: [aantal]
Cold calls / DMs: [aantal]
Calls geboekt: [aantal]
Actieve gesprekken: [aantal]
Follow-ups: [aantal]

Pijnpunten gehoord vandaag:
[Wat zeiden klanten? Welke problemen noemden ze letterlijk?]

Blokkades / wat kon beter:
[Wat hield je tegen vandaag?]
```

⏰ Deadline: **18:00 elke werkdag**
❌ Geen rapport = niet geteld voor leaderboard"""
        pin(dagrapport_id, dagrapport_format)
        print("  ✅ Dagrapport format vastgepind!")

    print("\n" + "="*55)
    print("✅ NEXTRIQ Discord v3.0 volledig aangemaakt!")
    print("="*55)
    print("""
Aangemaakt:
  ✅ 14 rollen (3 nieuw: Ink Setter, Platform Setter, Outreacher)
  ✅ 13 categorieën (4 nieuw: Marketing Middelen, Outreach, Ink Approved, Platform)
  ✅ 65+ kanalen met beschrijvingen en rechten
  ✅ Welkomstbericht vastgepind
  ✅ Dagrapport format vastgepind
  ✅ 10 voice kanalen

Volgende stappen:
  1. Geef jezelf de 🚀 Founder rol
  2. Geef Kim de 🛡️ Sales Manager rol
  3. Wijs Ink Setters de 🖤 Ink Setter rol toe
  4. Wijs Platform Setters de 🌐 Platform Setter rol toe
  5. Stel Zapier automatiseringen in
  6. Zet handboek-links in #handboeken
  7. Zet CRM-link (crmoas.vercel.app) in #systeem-updates
""")

if __name__ == "__main__":
    main()
