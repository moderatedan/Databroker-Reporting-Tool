# Deploying Lingo Bridge

Static site — two files (`index.html`, `dictionary.js`), any static host works.

## GitHub Pages (recommended)

```bash
git init
git add .
git commit -m "v2: 147-term credited dictionary, annotated translator, speech, sharing, history"
git branch -M main
git remote add origin https://github.com/moderatedan/hood-lingo-translator.git
git push -u origin main
```

Then **Settings → Pages → Deploy from a branch → main / (root)**.
Live at `https://moderatedan.github.io/hood-lingo-translator/` in about a
minute. Pages serves HTTPS, which the mic (Web Speech API) and clipboard
require.

## Netlify / Cloudflare Pages

Drag-and-drop at https://app.netlify.com/drop, or:

```bash
wrangler pages deploy . --project-name lingo-bridge
```

## Fully offline build (optional)

Download the three Google Fonts (Archivo Black, Source Serif 4, Inter) as
woff2, drop them in `fonts/`, and swap the `<link>` tags for local
`@font-face` rules. Everything else already runs offline. Voice input still
needs Chrome/Edge — it's a browser capability, not a network one.

## Repo settings that help this project find its people

- **Topics:** `slang`, `aave`, `dictionary`, `translator`, `linguistics`,
  `web-speech-api`, `glossary`
- **About:** "Living slang glossary & translator — origins credited on every
  entry. Community-editable."
- Enable **Issues** with a "new term / correction" template asking for:
  term, meaning, example sentence, where it's from, and how the contributor
  knows it.
- Pin the **house rules** (README → Contributing) in the PR template so
  review expectations are visible before anyone writes an entry.

## Post-deploy checklist

- [ ] Replace `moderatedan` in index.html (footer) and README.md;
      `Daniel Brummitt` in LICENSE
- [ ] Test the mic button on the deployed HTTPS URL (it won't work on
      plain http)
- [ ] Test a share link end-to-end: Share → open the `?q=` URL in a
      private window → auto-translation fires
- [ ] Screenshots for `docs/` (translate view, an entry card, the glossary)
- [ ] Tag it: `git tag v2.0.0 && git push --tags`
