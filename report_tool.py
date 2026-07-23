#!/usr/bin/env python3
"""
Databroker-Reporting-Tool — escalate when data brokers ignore your rights.

Where an opt-out tool asks brokers nicely, this tool handles what comes next:
drafting formal complaints to regulators (FTC, CFPB, state AGs, the
California CPPA, EU/UK data protection authorities), tracking statutory
response deadlines so you know the moment a broker is in violation, checking
state data-broker registries, and keeping an evidence log you can attach to
any complaint.

Pairs with the DataBrokerOptOut project: point `scan-optouts` at its
progress.json and every ignored request past its legal deadline becomes a
ready-to-file complaint.

Design honesty
--------------
* This tool never files anything for you — regulator forms require your
  identity and attestation. It drafts the narrative, opens the right form,
  and logs what you filed.
* "Auto-discovery" generates targeted search URLs to find which brokers list
  you; it does not scrape sites.
* Templates cite real statutes (CCPA/CPRA, GDPR) but are consumer-complaint
  letters, not legal advice. For actual disputes, talk to a lawyer or your
  state AG's office.
* Everything is stored locally in ./data (gitignored). The script makes no
  network requests — your browser does the talking.

Usage
-----
  python3 report_tool.py profile                 # one-time setup
  python3 report_tool.py channels                # list all reporting channels
  python3 report_tool.py discover --name "Jane Doe" --brokers brokers.json
  python3 report_tool.py track spokeo 2026-06-01 --law ccpa
  python3 report_tool.py deadlines               # who is past the deadline?
  python3 report_tool.py scan-optouts ../DataBrokerOptOut/data/progress.json
  python3 report_tool.py draft ftc spokeo --violation ignored_optout
  python3 report_tool.py file ftc spokeo         # draft + open the form
  python3 report_tool.py log ftc spokeo --case FTC-2026-12345
  python3 report_tool.py status                  # complaint dashboard
  python3 report_tool.py export complaints.csv
  python3 report_tool.py report-dead-url ftc     # community: fix a moved URL

License: MIT
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote, quote_plus

# --------------------------------------------------------------------------- #
# Paths & constants
# --------------------------------------------------------------------------- #

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTBOX_DIR = DATA_DIR / "outbox"
CHANNELS_FILE = BASE_DIR / "channels.json"
PROFILE_FILE = DATA_DIR / "profile.json"
TRACKING_FILE = DATA_DIR / "tracking.json"     # opt-out deadline tracking
COMPLAINTS_FILE = DATA_DIR / "complaints.json"  # filed complaints log

GITHUB_REPO = "moderatedan/Databroker-Reporting-Tool"

DATE_FMT = "%Y-%m-%d"

# Statutory response windows (days) for a deletion/opt-out request.
LAWS = {
    "ccpa": {"days": 45, "name": "CCPA/CPRA (California)",
             "cite": "Cal. Civ. Code § 1798.130(a)(2) — 45 days, extendable once with notice"},
    "gdpr": {"days": 30, "name": "GDPR (EU/UK)",
             "cite": "GDPR Art. 12(3) — one month, extendable with notice"},
    "vcdpa": {"days": 45, "name": "VCDPA (Virginia)", "cite": "Va. Code § 59.1-577(B) — 45 days"},
    "cpa": {"days": 45, "name": "CPA (Colorado)", "cite": "C.R.S. § 6-1-1306(2) — 45 days"},
    "ctdpa": {"days": 45, "name": "CTDPA (Connecticut)", "cite": "Conn. Gen. Stat. § 42-522 — 45 days"},
    "tdpsa": {"days": 45, "name": "TDPSA (Texas)", "cite": "Tex. Bus. & Com. Code § 541.052 — 45 days"},
}

VIOLATIONS = {
    "ignored_optout": "did not respond to my deletion/opt-out request within the statutory deadline",
    "refused": "refused a valid deletion/opt-out request without a lawful basis",
    "reappeared": "re-published my personal information after confirming its deletion",
    "no_optout_offered": "offers no functional opt-out or deletion mechanism",
    "dark_patterns": "uses obstructive design (dark patterns) to frustrate opt-out attempts",
    "unregistered": "operates as a data broker without the registration required in this state",
    "sold_after_optout": "continued selling/sharing my personal information after I opted out",
}

# --------------------------------------------------------------------------- #
# Legal templates — consumer complaint letters, not legal advice
# --------------------------------------------------------------------------- #

TEMPLATES = {
    # Sent TO the broker when a deadline lapses — the escalation warning shot.
    "broker_final_notice": """\
Subject: FINAL NOTICE — Overdue Response to Verified Consumer Request ({law_name})

To whom it may concern at {broker},

On {request_date} I submitted a verifiable consumer request asking you to
delete my personal information and opt me out of its sale or sharing.
{law_cite}. That deadline passed on {deadline_date}. As of {today},
{days_over} day(s) have elapsed beyond it and I have received no
substantive response.

This letter is my final notice before I file complaints with the relevant
regulators, including the Federal Trade Commission and my state Attorney
General{cppa_clause}.

To resolve this, within 10 business days please: (1) confirm deletion of my
personal information; (2) confirm I am opted out of any sale or sharing;
and (3) identify any service providers or downstream recipients notified.

Identifying information for my records: {full_name}, {emails},
{current_address}.

{full_name}
{today}
""",

    # Narrative for the FTC's report form.
    "ftc": """\
COMPLAINT NARRATIVE — for the FTC report form (reportfraud.ftc.gov)

Company: {broker}
Category: Data broker / privacy

On {request_date} I submitted a request to {broker} to delete my personal
information and opt out of its sale, using the mechanism the company itself
provides. The company {violation_text}.

{deadline_paragraph}I believe this conduct is an unfair or deceptive
practice: the company profits from publishing personal information about
consumers while failing to honor the removal process it advertises.

I request that the FTC record this complaint for enforcement purposes. I can
provide documentation, including a copy of my original request{evidence_note}.

Filed by: {full_name}, {current_address}
""",

    # Narrative for a state AG consumer complaint form.
    "state_ag": """\
COMPLAINT NARRATIVE — for your state Attorney General's consumer complaint form

Business complained about: {broker}
Nature of complaint: Data broker — failure to honor privacy rights

I am a resident of {state}. On {request_date} I asked {broker} to delete my
personal information and stop selling or sharing it. The company
{violation_text}.

{deadline_paragraph}The company publishes and/or sells personal information
about me — including contact details and address history — without my
consent, and its advertised removal process does not function as
represented.

I ask your office to record this complaint, contact the business, and
consider it in any broader enforcement review of data broker practices in
{state}. Documentation is available on request{evidence_note}.

Complainant: {full_name}, {current_address}, {emails}
""",

    # Complaint to the California Privacy Protection Agency.
    "cppa": """\
COMPLAINT NARRATIVE — for the CPPA complaint form (cppa.ca.gov)

Business: {broker}
Alleged violation: CCPA/CPRA consumer request non-compliance

On {request_date} I submitted a verifiable consumer request to {broker} to
delete my personal information (Cal. Civ. Code § 1798.105) and to opt out of
its sale or sharing (§ 1798.120). The business {violation_text}.

{deadline_paragraph}Under § 1798.130(a)(2), a business must respond within
45 days of a verifiable request. I have received no compliant response.

{registry_paragraph}I request that the Agency review this business's
compliance with the CCPA/CPRA and, if applicable, the Delete Act
(SB 362). Documentation is available on request{evidence_note}.

Complainant: {full_name} (California resident), {current_address}
""",

    # GDPR Article 77 complaint to a Data Protection Authority.
    "dpa": """\
COMPLAINT — Article 77 GDPR, to the supervisory authority

Data controller: {broker}
Complainant: {full_name}, {current_address}

1. On {request_date} I submitted a request to the controller under Article
   17 GDPR (right to erasure), asking it to erase my personal data and cease
   processing, including for direct marketing (Article 21).

2. Under Article 12(3), the controller was required to respond within one
   month, i.e. by {deadline_date}. The controller {violation_text}.

3. I therefore lodge this complaint under Article 77 and ask the authority
   to investigate, order erasure under Article 58(2), and consider
   corrective measures.

4. Evidence available: copy of the original request, proof of submission,
   and the controller's listing of my data{evidence_note}.

{full_name}
{today}
""",

    # Report an unregistered broker to a state registry authority.
    "registry": """\
REPORT — Possible unregistered data broker

To: {channel_name}

I wish to report that {broker} appears to meet your state's definition of a
data broker — it knowingly collects and sells or licenses to third parties
the personal information of consumers with whom it has no direct
relationship — but does not appear in the current registry.

Evidence: the company's website offers detailed personal records (contact
information, addresses, relatives) about members of the public, including
me, for a fee. My details: {full_name}, {current_address}.

Please review whether this business is required to register, and apply any
penalties for unregistered operation that your statute provides.

{full_name}
{today}
""",
}


# --------------------------------------------------------------------------- #
# Storage
# --------------------------------------------------------------------------- #


def ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTBOX_DIR.mkdir(exist_ok=True)


def load_json(path: Path, default):
    if path.exists():
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    return default


def save_json(path: Path, data) -> None:
    ensure_dirs()
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def load_channels() -> list[dict]:
    if not CHANNELS_FILE.exists():
        sys.exit("channels.json not found — restore it from the repository.")
    return load_json(CHANNELS_FILE, {}).get("channels", [])


def get_channel(channel_id: str) -> dict:
    for ch in load_channels():
        if ch["id"] == channel_id:
            return ch
    ids = ", ".join(c["id"] for c in load_channels())
    sys.exit(f"Unknown channel '{channel_id}'. Known: {ids}")


def load_profile() -> dict:
    return load_json(PROFILE_FILE, {})


def profile_fields(profile: dict) -> dict:
    join = lambda xs: ", ".join(xs) if xs else "—"
    return {
        "full_name": profile.get("full_name", "—"),
        "emails": join(profile.get("emails", [])),
        "current_address": profile.get("current_address", "—"),
        "state": profile.get("state", "—"),
        "today": datetime.now().strftime("%B %d, %Y"),
    }


# --------------------------------------------------------------------------- #
# Deadline tracking
# --------------------------------------------------------------------------- #


def add_tracking(broker: str, request_date: str, law: str) -> dict:
    try:
        req = datetime.strptime(request_date, DATE_FMT)
    except ValueError:
        sys.exit(f"Date must be YYYY-MM-DD, got '{request_date}'")
    if law not in LAWS:
        sys.exit(f"Unknown law '{law}'. Choose from: {', '.join(LAWS)}")
    deadline = req + timedelta(days=LAWS[law]["days"])
    tracking = load_json(TRACKING_FILE, {})
    tracking[broker.lower()] = {
        "broker": broker,
        "request_date": request_date,
        "law": law,
        "deadline": deadline.strftime(DATE_FMT),
    }
    save_json(TRACKING_FILE, tracking)
    return tracking[broker.lower()]


def overdue_entries() -> list[dict]:
    tracking = load_json(TRACKING_FILE, {})
    today = datetime.now()
    out = []
    for rec in tracking.values():
        deadline = datetime.strptime(rec["deadline"], DATE_FMT)
        rec = dict(rec)
        rec["days_over"] = (today - deadline).days
        rec["overdue"] = rec["days_over"] > 0
        out.append(rec)
    return sorted(out, key=lambda r: -r["days_over"])


# --------------------------------------------------------------------------- #
# Drafting
# --------------------------------------------------------------------------- #


def channel_template(channel: dict) -> str:
    kind = channel["kind"]
    if channel["id"] == "ftc":
        return "ftc"
    if channel["id"] == "cfpb":
        return "ftc"  # same narrative shape works for the CFPB form
    if channel["id"] == "cppa":
        return "cppa"
    if kind == "state-ag":
        return "state_ag"
    if kind == "dpa":
        return "dpa"
    if kind == "registry":
        return "registry"
    return "state_ag"


def build_draft(channel: dict, broker: str, violation: str,
                request_date: str | None) -> str:
    profile = load_profile()
    if not profile:
        sys.exit("Set up your profile first:  python3 report_tool.py profile")
    fields = profile_fields(profile)
    fields["broker"] = broker
    fields["channel_name"] = channel["name"]
    fields["violation_text"] = VIOLATIONS.get(violation, violation)
    fields["evidence_note"] = (
        " (see also my complaint log maintained with the "
        "Databroker-Reporting-Tool)")

    # Deadline context if this broker is tracked
    tracking = load_json(TRACKING_FILE, {}).get(broker.lower())
    if tracking:
        law = LAWS[tracking["law"]]
        fields["request_date"] = tracking["request_date"]
        fields["deadline_date"] = tracking["deadline"]
        days_over = (datetime.now()
                     - datetime.strptime(tracking["deadline"], DATE_FMT)).days
        fields["days_over"] = max(days_over, 0)
        fields["law_name"] = law["name"]
        fields["law_cite"] = law["cite"]
        fields["deadline_paragraph"] = (
            f"The applicable law ({law['name']}) required a response by "
            f"{tracking['deadline']}; that deadline has passed"
            + (f" by {days_over} days" if days_over > 0 else "") + ". \n\n")
    else:
        fields["request_date"] = request_date or "[DATE OF YOUR REQUEST]"
        fields["deadline_date"] = "[STATUTORY DEADLINE]"
        fields["days_over"] = "[N]"
        fields["law_name"] = "the applicable state privacy law"
        fields["law_cite"] = ("The applicable law requires a response within "
                              "the statutory period (typically 45 days)")
        fields["deadline_paragraph"] = ""

    fields["cppa_clause"] = (
        " and the California Privacy Protection Agency"
        if fields["state"].lower() in ("ca", "california") else "")
    fields["registry_paragraph"] = (
        "" if violation != "unregistered" else
        "Additionally, this business does not appear in the Delete Act data "
        "broker registry despite appearing to meet the statutory "
        "definition.\n\n")

    tpl = TEMPLATES[channel_template(channel)]
    return tpl.format(**fields)


def write_draft(channel: dict, broker: str, text: str) -> Path:
    ensure_dirs()
    fname = (OUTBOX_DIR /
             f"{channel['id']}-{broker.lower().replace(' ', '_')}-"
             f"{datetime.now():%Y%m%d-%H%M%S}.txt")
    fname.write_text(text, encoding="utf-8")
    return fname


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #


def cmd_profile(args) -> None:
    profile = load_profile()
    if args.show:
        print(json.dumps(profile, indent=2) if profile else
              "No profile yet. Run:  python3 report_tool.py profile")
        return
    print("Info used to fill complaint templates. Stored ONLY in "
          "./data/profile.json (gitignored).")
    print("Press Enter to keep the value in [brackets].\n")

    def ask(prompt, key, is_list=False):
        current = profile.get(key, [] if is_list else "")
        shown = ", ".join(current) if is_list else current
        raw = input(f"{prompt} [{shown}]: ").strip()
        if not raw:
            return current
        return ([x.strip() for x in raw.split(",") if x.strip()]
                if is_list else raw)

    profile["full_name"] = ask("Full legal name", "full_name")
    profile["emails"] = ask("Email addresses (comma-separated)", "emails", True)
    profile["current_address"] = ask("Current address", "current_address")
    profile["state"] = ask("State of residence (e.g. California)", "state")
    save_json(PROFILE_FILE, profile)
    print(f"\nSaved to {PROFILE_FILE}")


def cmd_channels(args) -> None:
    channels = load_channels()
    if args.kind:
        channels = [c for c in channels if c["kind"] == args.kind]
    kinds = sorted({c["kind"] for c in load_channels()})
    print(f"{'ID':<16} {'Kind':<24} Channel")
    print("-" * 84)
    for c in channels:
        print(f"{c['id']:<16} {c['kind']:<24} {c['name']}")
        print(f"{'':<16} {'':<24} good for: {', '.join(c['good_for'])}")
    print(f"\n{len(channels)} channel(s). Kinds: {', '.join(kinds)}")


def cmd_discover(args) -> None:
    """Generate targeted search URLs to find which brokers list you."""
    name = args.name or load_profile().get("full_name")
    if not name or name == "—":
        sys.exit("Provide --name or set up your profile first.")

    domains: list[str] = []
    if args.brokers:
        data = load_json(Path(args.brokers), {})
        for b in data.get("brokers", []):
            url = b.get("optout_url", "")
            if "//" in url:
                domains.append(url.split("/")[2].removeprefix("www."))
    if not domains:
        # A compact starter set; point --brokers at DataBrokerOptOut's
        # brokers.json for the full 40-site sweep.
        domains = ["spokeo.com", "whitepages.com", "beenverified.com",
                   "truepeoplesearch.com", "fastpeoplesearch.com",
                   "radaris.com", "mylife.com", "peoplefinders.com",
                   "usphonebook.com", "clustrmaps.com"]

    print(f"Discovery sweep for “{name}” across {len(domains)} broker "
          f"site(s):\n")
    urls = []
    for d in sorted(set(domains)):
        u = f"https://duckduckgo.com/?q={quote_plus(f'site:{d} {name}')}"
        urls.append((d, u))
        print(f"  {d:<28} {u}")

    checklist = "\n".join(
        f"- [ ] {d} — {u}" for d, u in urls)
    ensure_dirs()
    out = DATA_DIR / f"discovery-{datetime.now():%Y%m%d}.md"
    out.write_text(f"# Discovery checklist — {name} — "
                   f"{datetime.now():%Y-%m-%d}\n\n{checklist}\n",
                   encoding="utf-8")
    print(f"\nChecklist saved: {out}")
    if args.open:
        print("Opening in browser (in batches — close tabs as you check)...")
        for _, u in urls:
            webbrowser.open(u)
    else:
        print("Re-run with --open to launch all searches in your browser.")


def cmd_track(args) -> None:
    rec = add_tracking(args.broker, args.request_date, args.law)
    law = LAWS[rec["law"]]
    print(f"Tracking {rec['broker']}: request {rec['request_date']} under "
          f"{law['name']}")
    print(f"  Statutory deadline: {rec['deadline']}  ({law['cite']})")
    print("  Run `deadlines` any time to see who's overdue.")


def cmd_deadlines(_args) -> None:
    entries = overdue_entries()
    if not entries:
        print("No tracked requests. Add one:\n"
              "  python3 report_tool.py track <broker> <YYYY-MM-DD> --law ccpa")
        return
    print(f"{'Broker':<24} {'Requested':<12} {'Law':<8} {'Deadline':<12} Status")
    print("-" * 78)
    for r in entries:
        status = (f"OVERDUE by {r['days_over']}d — file a complaint!"
                  if r["overdue"] else
                  f"{-r['days_over']}d remaining")
        print(f"{r['broker']:<24} {r['request_date']:<12} {r['law']:<8} "
              f"{r['deadline']:<12} {status}")
    overdue = [r for r in entries if r["overdue"]]
    if overdue:
        print(f"\n{len(overdue)} broker(s) past the legal deadline. Next steps:")
        print("  python3 report_tool.py draft broker_final_notice <broker>   # warning letter")
        print("  python3 report_tool.py file ftc <broker>                    # federal complaint")
        print("  python3 report_tool.py file ag_<state> <broker>             # your state AG")


def cmd_scan_optouts(args) -> None:
    """Import DataBrokerOptOut's progress.json and track everything submitted."""
    path = Path(args.progress)
    if not path.exists():
        sys.exit(f"Not found: {path}\nExpected DataBrokerOptOut's "
                 "data/progress.json")
    progress = load_json(path, {})
    imported = 0
    for broker_id, rec in progress.items():
        status = rec.get("status")
        if status in ("submitted", "awaiting_confirmation"):
            ts = rec.get("updated", "")[:10]
            try:
                datetime.strptime(ts, DATE_FMT)
            except ValueError:
                continue
            add_tracking(broker_id, ts, args.law)
            imported += 1
    print(f"Imported {imported} in-flight opt-out(s) under "
          f"{LAWS[args.law]['name']} deadlines.")
    if imported:
        cmd_deadlines(None)


def cmd_draft(args) -> None:
    if args.channel == "broker_final_notice":
        profile = load_profile()
        if not profile:
            sys.exit("Set up your profile first: python3 report_tool.py profile")
        fake_channel = {"id": "broker_final_notice", "kind": "letter",
                        "name": "Final notice to broker"}
        fields_needed = load_json(TRACKING_FILE, {}).get(args.broker.lower())
        if not fields_needed and not args.request_date:
            sys.exit("Track this broker first (`track`) or pass "
                     "--request-date YYYY-MM-DD.")
        f = profile_fields(profile)
        rec = fields_needed or {
            "request_date": args.request_date,
            "law": args.law,
            "deadline": (datetime.strptime(args.request_date, DATE_FMT)
                         + timedelta(days=LAWS[args.law]["days"])
                         ).strftime(DATE_FMT),
        }
        law = LAWS[rec["law"]]
        days_over = (datetime.now()
                     - datetime.strptime(rec["deadline"], DATE_FMT)).days
        text = TEMPLATES["broker_final_notice"].format(
            broker=args.broker, law_name=law["name"], law_cite=law["cite"],
            request_date=rec["request_date"], deadline_date=rec["deadline"],
            days_over=max(days_over, 0),
            cppa_clause=(" and the California Privacy Protection Agency"
                         if f["state"].lower() in ("ca", "california") else ""),
            **{k: f[k] for k in
               ("full_name", "emails", "current_address", "today")})
        path = write_draft(fake_channel, args.broker, text)
    else:
        channel = get_channel(args.channel)
        text = build_draft(channel, args.broker, args.violation,
                           args.request_date)
        path = write_draft(channel, args.broker, text)
    print(text)
    print(f"--- draft saved: {path}")


def cmd_file(args) -> None:
    channel = get_channel(args.channel)
    text = build_draft(channel, args.broker, args.violation, args.request_date)
    path = write_draft(channel, args.broker, text)
    print(f"Draft narrative saved: {path}")
    try:
        import tkinter
        r = tkinter.Tk(); r.withdraw(); r.clipboard_clear()
        r.clipboard_append(text); r.update(); r.destroy()
        print("Narrative copied to clipboard — paste it into the form.")
    except Exception:
        print("(Clipboard unavailable — copy the narrative from the file.)")
    print(f"Opening {channel['name']}: {channel['url']}")
    webbrowser.open(channel["url"])
    print("\nAfter submitting, log it so the record is complete:")
    print(f"  python3 report_tool.py log {channel['id']} {args.broker} "
          "--case <confirmation number>")


def cmd_log(args) -> None:
    get_channel(args.channel)  # validate
    complaints = load_json(COMPLAINTS_FILE, [])
    complaints.append({
        "ts": datetime.now().strftime(DATE_FMT),
        "channel": args.channel,
        "broker": args.broker,
        "case": args.case or "",
        "violation": args.violation,
        "status": "filed",
        "note": args.note or "",
    })
    save_json(COMPLAINTS_FILE, complaints)
    print(f"Logged: {args.broker} → {args.channel}"
          + (f" (case {args.case})" if args.case else ""))


def cmd_status(_args) -> None:
    complaints = load_json(COMPLAINTS_FILE, [])
    entries = overdue_entries()
    overdue = [r for r in entries if r["overdue"]]
    print("\nDatabroker-Reporting-Tool — status\n")
    print(f"  Tracked requests:      {len(entries)}")
    print(f"  Past legal deadline:   {len(overdue)}")
    print(f"  Complaints filed:      {len(complaints)}")
    if complaints:
        by_channel: dict[str, int] = {}
        for c in complaints:
            by_channel[c["channel"]] = by_channel.get(c["channel"], 0) + 1
        for ch, n in sorted(by_channel.items(), key=lambda kv: -kv[1]):
            print(f"    {ch:<14} {n}")
    if overdue:
        print("\n  ⚠ Overdue brokers ready to escalate — run `deadlines`.")
    print()


def cmd_export(args) -> None:
    complaints = load_json(COMPLAINTS_FILE, [])
    with open(args.path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "channel", "broker", "case", "violation",
                    "status", "note"])
        for c in complaints:
            w.writerow([c["ts"], c["channel"], c["broker"], c["case"],
                        c["violation"], c["status"], c["note"]])
    print(f"Exported {len(complaints)} complaint(s) to {args.path}")


def cmd_report_dead_url(args) -> None:
    """Community feature: open a prefilled GitHub issue for a moved URL."""
    ch = get_channel(args.channel)
    title = f"Dead/moved URL: {ch['id']} ({ch['name']})"
    body = (f"**Channel:** `{ch['id']}`\n"
            f"**Current URL in channels.json:** {ch['url']}\n"
            f"**What happens:** <!-- 404 / redirect / form moved -->\n"
            f"**Working URL (if known):** \n"
            f"**Date checked:** {datetime.now():%Y-%m-%d}\n")
    url = (f"https://github.com/{GITHUB_REPO}/issues/new"
           f"?title={quote(title)}&body={quote(body)}")
    print(f"Opening a prefilled issue for {ch['name']}...")
    print(url)
    webbrowser.open(url)


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #


def main(argv=None) -> None:
    p = argparse.ArgumentParser(
        prog="report_tool.py",
        description="Escalate when data brokers ignore your rights.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command")

    sp = sub.add_parser("profile", help="set up or show your info")
    sp.add_argument("--show", action="store_true")
    sp.set_defaults(fn=cmd_profile)

    sp = sub.add_parser("channels", help="list reporting channels")
    sp.add_argument("--kind", help="filter: federal, state-ag, "
                    "state-privacy-regulator, registry, dpa")
    sp.set_defaults(fn=cmd_channels)

    sp = sub.add_parser("discover",
                        help="generate searches to find where you're listed")
    sp.add_argument("--name", help="name to search (default: profile name)")
    sp.add_argument("--brokers",
                    help="path to a brokers.json (e.g. from DataBrokerOptOut)")
    sp.add_argument("--open", action="store_true",
                    help="open every search in the browser")
    sp.set_defaults(fn=cmd_discover)

    sp = sub.add_parser("track", help="track a request's legal deadline")
    sp.add_argument("broker")
    sp.add_argument("request_date", help="YYYY-MM-DD the request was submitted")
    sp.add_argument("--law", choices=list(LAWS), default="ccpa")
    sp.set_defaults(fn=cmd_track)

    sp = sub.add_parser("deadlines", help="show deadline status for all tracked")
    sp.set_defaults(fn=cmd_deadlines)

    sp = sub.add_parser("scan-optouts",
                        help="import DataBrokerOptOut progress.json")
    sp.add_argument("progress", help="path to progress.json")
    sp.add_argument("--law", choices=list(LAWS), default="ccpa")
    sp.set_defaults(fn=cmd_scan_optouts)

    sp = sub.add_parser("draft", help="print + save a complaint draft")
    sp.add_argument("channel",
                    help="channel id from `channels`, or broker_final_notice")
    sp.add_argument("broker")
    sp.add_argument("--violation", choices=list(VIOLATIONS),
                    default="ignored_optout")
    sp.add_argument("--request-date", dest="request_date",
                    help="YYYY-MM-DD if the broker isn't tracked")
    sp.add_argument("--law", choices=list(LAWS), default="ccpa")
    sp.set_defaults(fn=cmd_draft)

    sp = sub.add_parser("file", help="draft, copy, and open the channel's form")
    sp.add_argument("channel")
    sp.add_argument("broker")
    sp.add_argument("--violation", choices=list(VIOLATIONS),
                    default="ignored_optout")
    sp.add_argument("--request-date", dest="request_date")
    sp.set_defaults(fn=cmd_file)

    sp = sub.add_parser("log", help="record a complaint you filed")
    sp.add_argument("channel")
    sp.add_argument("broker")
    sp.add_argument("--case", help="confirmation/case number")
    sp.add_argument("--violation", choices=list(VIOLATIONS),
                    default="ignored_optout")
    sp.add_argument("-n", "--note")
    sp.set_defaults(fn=cmd_log)

    sp = sub.add_parser("status", help="dashboard")
    sp.set_defaults(fn=cmd_status)

    sp = sub.add_parser("export", help="export complaint log to CSV")
    sp.add_argument("path")
    sp.set_defaults(fn=cmd_export)

    sp = sub.add_parser("report-dead-url",
                        help="open a prefilled GitHub issue for a moved URL")
    sp.add_argument("channel")
    sp.set_defaults(fn=cmd_report_dead_url)

    args = p.parse_args(argv)
    if not args.command:
        p.print_help()
        return
    args.fn(args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.stderr.close()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)
