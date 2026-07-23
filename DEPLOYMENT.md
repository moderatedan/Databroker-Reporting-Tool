# Publishing Databroker-Reporting-Tool

A local CLI — "deployment" means publishing the repo well.

## Push to GitHub

```bash
git init
git add .
git commit -m "v2: 24 channels, statutory deadline tracking, legal templates, DataBrokerOptOut integration"
git branch -M main
git remote add origin https://github.com/moderatedan/Databroker-Reporting-Tool.git
git push -u origin main
```

Check nothing personal is staged:

```bash
git status --ignored | grep data/   # data/ must be ignored
```

## Critical: set the GitHub repo constant

`report-dead-url` opens prefilled issues against the repo named in
`report_tool.py` → `GITHUB_REPO = "moderatedan/Databroker-Reporting-Tool"`.
Update it or the community feature points at nothing.

## Recommended repo settings

- **Topics:** `privacy`, `data-brokers`, `ccpa`, `gdpr`, `ftc`,
  `consumer-rights`, `python`
- **About:** "Escalation toolkit for ignored data broker opt-outs: deadline
  tracking, regulator-ready complaints, 24 channels. Zero dependencies."
- Enable **Issues**; add a `dead-url.md` issue template with fields:
  channel id, old URL, what happens, working URL, date checked — matching
  what `report-dead-url` prefills.
- Link the companion repo (DataBrokerOptOut) in the README and vice versa —
  the pairing is the story.

## Post-publish checklist

- [ ] Replace `moderatedan` (README.md + GITHUB_REPO constant),
      `Daniel Brummitt` (LICENSE)
- [ ] Spot-check the channel URLs you personally can verify — regulator
      forms move, and accuracy is the product
- [ ] Run the workflow once end-to-end against a real tracked request
- [ ] Screenshots for `docs/` (deadlines table, a draft, status dashboard)
- [ ] Tag it: `git tag v2.0.0 && git push --tags`
