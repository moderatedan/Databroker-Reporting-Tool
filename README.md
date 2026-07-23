# 🗣️ Lingo Bridge (hood-lingo-translator)

> A living glossary and translator for American and UK street slang — origins credited on every entry, community-editable by design.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Terms](https://img.shields.io/badge/dictionary-147%20terms-blue.svg)
![Dependencies](https://img.shields.io/badge/runtime%20deps-zero-brightgreen.svg)
![Made with](https://img.shields.io/badge/made%20with-vanilla%20JS-f7df1e.svg)

Paste (or speak) a sentence full of slang and Lingo Bridge highlights every term it knows, renders a plain-English version, and puts the full dictionary entry — meaning, part of speech, example, and **origin** — one tap away. Or skip the translator and browse the glossary like the reference work it is.

**The stance:** most of this vocabulary originates in African-American Vernacular English and in specific scenes and cities — hip-hop, ballroom culture, London's Multicultural English, Jamaican Patois. This project documents and credits that language; it doesn't costume it. That's written into the app, the dictionary's house rules, and the contribution policy below.

---

## ✨ Features

- **147-term community dictionary** — `dictionary.js` is a single, readable file of structured entries: term, variants, part of speech, short gloss, full definition, usage example, origin credit, and tags. Regional coverage includes AAVE staples, NY/Bay/Philly/Atlanta regionalisms, UK roadman vocabulary, and internet-era coinage. Growing it is a one-line pull request.
- **Two-layer translation** — an *annotated* view (original text with tappable highlights that open full dictionary entries) and a *plain English* rendering (glosses substituted in place, capitalization and punctuation preserved). Multi-word phrases like "no cap" and "understood the assignment" match before their parts.
- **Speech, both directions** — 🎙 voice input via the Web Speech API (Chrome/Edge; graceful fallback elsewhere), and 🔊 read-aloud for translations and for any dictionary entry (term + definition + example).
- **Sharing** — native share sheet where supported, shareable `?q=` links that auto-translate on open, and one-tap copy.
- **History** — session history of translations with tap-to-rerun, downloadable as a `.txt`. Deliberately not persisted: nothing is stored after the tab closes.
- **Glossary browser** — instant search across terms, meanings, and origins; filter chips (AAVE / Hip-hop / Ballroom / UK / Internet / NY / Bay Area); a deterministic word-of-the-day everyone sees.
- **Modern UI** — editorial dictionary-entry cards, dark/light mode following your OS with a manual toggle, keyboard-accessible highlights, reduced-motion respected, single HTML file.

## 📸 Screenshots

> _Add your screenshots here:_

| Translate (annotated) | Entry card | Glossary browser |
|---|---|---|
| ![Translate](docs/screenshot-translate.png) | ![Entry](docs/screenshot-entry.png) | ![Glossary](docs/screenshot-glossary.png) |

## 🚀 Getting started

```bash
git clone https://github.com/moderatedan/hood-lingo-translator.git
cd hood-lingo-translator
python3 -m http.server 8080     # or just open index.html
# → http://localhost:8080
```

**Dependencies:** none at runtime — vanilla HTML/CSS/JS. The only external requests are Google Fonts (Archivo Black, Source Serif 4, Inter), which degrade gracefully to system fonts offline; vendor them locally if you want a fully offline build. Voice input requires a browser with the Web Speech API (Chrome/Edge); everything else works everywhere.

## 📖 Usage

1. **Translate** — paste or 🎙 speak a sentence, hit Translate (or Ctrl/Cmd+Enter). Tap any highlighted term for its full entry; use 🔊 to hear the plain-English version.
2. **Glossary** — search or filter by origin; every entry card has its own read-aloud button.
3. **Share** — the Share button produces a link like `index.html?q=no+cap+that+slaps` that auto-translates when opened.
4. **History** — revisit, rerun, or download this session's translations.

### An honest note on accuracy

Word-level gloss substitution is transparent and auditable, but it isn't grammar-aware: "the mandem are linking" becomes "the the guys are meet up," and ordinary words that double as slang ("bet," "safe," "peak") can be flagged in plain sentences. The annotated view — highlights plus full entries — is the primary product; the plain rendering is a fast gloss, and the UI says so. Smarter sense disambiguation is on the roadmap.

## 🤝 Contributing — house rules

The dictionary is the project. To add or fix a term, edit `dictionary.js` and open a PR. Four rules, enforced in review:

1. **Define, don't mock.** Write the definition the way a good dictionary would.
2. **Credit origins.** Every entry names where the term comes from — AAVE, a city, a scene, a subculture. "Origin: internet" is a last resort, not a default.
3. **No slurs**, and no terms whose primary use is demeaning a group.
4. **Keep glosses short** — they get substituted into sentences, so the first alternative before any `/` should read naturally in place.

Entry shape:

```js
{ term: "no cap", variants: ["nocap"], pos: "phrase",
  gloss: "no lie",
  def: "Truthfully; without exaggeration. 'Cap' means a lie...",
  example: "That was the best meal I've had all year, no cap.",
  origin: "AAVE / Atlanta hip-hop", tags: ["truth"] }
```

Slang moves fast and meanings drift by region — corrections from people who actually use these terms are the most valuable PRs this repo can get.

## 🗺️ Roadmap

- [ ] Word-sense disambiguation for double-duty words (bet/safe/peak/mad)
- [ ] Per-entry "heard it in" citations (songs, shows) with links
- [ ] More regions: Toronto, Houston, Chicago, Miami/Spanglish
- [ ] Quiz mode built from the glossary

## 📄 License

[MIT](LICENSE). The language itself belongs to the communities that made it.
