# 📣 Databroker-Reporting-Tool

> Opting out asks nicely. This tool handles what happens when they ignore you: statutory deadline tracking, regulator-ready complaint drafts, state registry checks, and an evidence log — across 24 reporting channels.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)
![Channels](https://img.shields.io/badge/reporting%20channels-24-orange.svg)

Data brokers are legally required to honor deletion and opt-out requests — the CCPA/CPRA gives them 45 days, the GDPR one month, and a growing list of state laws (Virginia, Colorado, Connecticut, Texas...) set their own clocks. Most people never track the clock, so brokers face no consequence for ignoring requests. This tool makes the clock — and the escalation — automatic.

**Design honesty:** the tool never files anything for you (regulator forms require your identity and attestation) and never scrapes broker sites. It drafts the narrative, copies it to your clipboard, opens the right form, tracks the deadlines, and keeps the record. Templates cite real statutes but are consumer-complaint letters, **not legal advice** — for actual disputes, talk to a lawyer or your state AG's office.

---

## ✨ Features

- **24 reporting channels** (`channels.json`) — FTC, CFPB (for background-check/FCRA-adjacent brokers), the California Privacy Protection Agency, 13 state Attorneys General plus a directory covering all 50, the four US data broker **registries** (California Delete Act, Vermont, Texas, Oregon), and EU/UK **data protection authorities** (ICO, Irish DPC, CNIL, EDPB directory) for GDPR Article 77 complaints. Each channel lists what it's good for.
- **Legal templates, auto-filled** — five statute-citing drafts: a final-notice letter to the broker (CCPA § 1798.105/130), FTC/CFPB complaint narratives, state AG narratives, CPPA complaints (including Delete Act non-registration), and GDPR Art. 77 complaints to a DPA. Seven violation types from `ignored_optout` to `dark_patterns` to `unregistered`.
- **Statutory deadline tracking** — `track spokeo 2026-05-01 --law ccpa` computes the legal response deadline; `deadlines` shows exactly who is overdue by how many days and what to file next. Supported clocks: CCPA/CPRA, GDPR, VCDPA, CPA, CTDPA, TDPSA.
- **DataBrokerOptOut integration** — `scan-optouts path/to/progress.json` imports every in-flight request from the companion [DataBrokerOptOut](https://github.com/moderatedan/DataBrokerOptOut) project and puts it on a legal clock automatically. Opt out with one tool; escalate with the other.
- **Auto-discovery** — generates site-scoped searches for your name across any broker list (point it at DataBrokerOptOut's 40-broker `brokers.json`), saves a Markdown checklist, and optionally opens every search in your browser. No scraping.
- **Complaint log & evidence trail** — every filed complaint recorded with channel, broker, case number, and violation; dashboard and CSV export for the paper trail regulators love.
- **Community features** — `channels.json` is community-maintained; `report-dead-url <channel>` opens a prefilled GitHub issue the moment a regulator moves a form, and the issue template captures exactly what maintainers need. Regulator URLs rot — the community keeps this accurate.
- **Zero dependencies, local-only** — pure standard library; all data in `./data/` (gitignored); the script itself makes no network requests.

## 📸 Screenshots

> _Add your screenshots here:_

| Deadlines view | Draft output | Status dashboard |
|---|---|---|
| ![Deadlines](docs/screenshot-deadlines.png) | ![Draft](docs/screenshot-draft.png) | ![Status](docs/screenshot-status.png) |

## 🚀 Installation

```bash
git clone https://github.com/moderatedan/Databroker-Reporting-Tool.git
cd Databroker-Reporting-Tool
python3 report_tool.py    # zero dependencies — prints help
```

Requires Python 3.9+.

## 📖 Usage

### The escalation workflow

```bash
# 1. One-time setup (stored locally only)
python3 report_tool.py profile

# 2. Put your requests on the legal clock
python3 report_tool.py track spokeo 2026-05-01 --law ccpa
#    ...or import everything from DataBrokerOptOut in one shot:
python3 report_tool.py scan-optouts ../DataBrokerOptOut/data/progress.json

# 3. Watch the clock
python3 report_tool.py deadlines
#    Spokeo    2026-05-01   ccpa   2026-06-15   OVERDUE by 38d — file a complaint!

# 4. Fire the warning shot (often enough by itself)
python3 report_tool.py draft broker_final_notice spokeo

# 5. Escalate to regulators — draft is copied, form opens in browser
python3 report_tool.py file ftc spokeo
python3 report_tool.py file ag_ca spokeo
python3 report_tool.py file cppa spokeo --violation sold_after_optout

# 6. Keep the record
python3 report_tool.py log ftc spokeo --case FTC-2026-12345
python3 report_tool.py status
python3 report_tool.py export complaints.csv
```

### Other commands

```bash
python3 report_tool.py channels                    # all 24 channels
python3 report_tool.py channels --kind registry    # just the registries
python3 report_tool.py discover --brokers ../DataBrokerOptOut/brokers.json --open
python3 report_tool.py draft cppa radaris --violation unregistered
python3 report_tool.py report-dead-url ftc         # community URL fix
```

## ⚖️ Which channel, when?

| Situation | Channel(s) |
|---|---|
| Broker ignored a request past the deadline | `broker_final_notice`, then `ftc` + your state AG |
| You're a California resident | add `cppa` — the dedicated privacy regulator |
| Broker feeds background/tenant checks | `cfpb` (FCRA angle — companies must respond individually) |
| Broker isn't in a state registry | `ca_registry` / `vt_registry` / `tx_registry` / `or_registry` + that state's AG, `--violation unregistered` |
| You're in the EU/UK | your DPA (`ico_uk`, `dpc_ie`, `cnil_fr`, or the `edpb_directory`) — Art. 77 |

One well-documented complaint rarely moves a regulator; a pattern of them does. That's why the log, the CSV export, and filing with **multiple** channels matter.

## 🤝 Contributing

The highest-value PRs maintain `channels.json`: regulator forms move constantly, and new state privacy laws (and registries) arrive every year. The `report-dead-url` command turns "I hit a 404" into a prefilled issue in one step. Adding a new state's AG, a new registry, or a new statutory clock to `LAWS` are all one-entry PRs.

## ⚠️ Not legal advice

This tool generates consumer complaints — something every consumer can file themselves — and cites statutes for accuracy. It is not a law firm and nothing here is legal advice. Statutory windows can be extended with notice (both CCPA and GDPR allow it), exemptions exist, and laws change. For disputes with real stakes, consult a lawyer or your state Attorney General's consumer division.

## 📄 License

[MIT](LICENSE)
