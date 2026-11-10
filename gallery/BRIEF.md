# Build brief (shared by all builders)

You are hand-crafting 10 of 100 standalone HTML showpieces. Every one of the 100 has a different
concept, aesthetic and technique; yours are listed in your prompt. Quality over speed.

Rules for every file:
- Write to /home/user/stageculture-ai-bot/gallery/<NN-slug>.html exactly as named. One file each, fully
  self-contained: inline CSS + JS only. NO external requests at all (no CDNs, no web fonts, no remote
  images). Use system font stacks chosen deliberately (serif / mono / condensed / rounded etc.), inline
  SVG, canvas, CSS gradients, SVG filters, WebAudio (start audio only after a user gesture).
- It must look stunning: a real art-directed piece, not a demo. Deliberate palette, typography with
  strong hierarchy, composition, texture/depth, motion with purpose. Commit fully to the named style.
  Avoid the generic "dark page + purple gradient + centered card" look unless the concept is that.
- No repetition: do not reuse layout skeletons, palettes, or code structure between your own 10 files.
  Each should feel like it was made by a different studio.
- Original content only: invented names, places, copy. No real brands, people, logos, or copyrighted
  characters. Write real, evocative copy — no lorem ipsum.
- Where the concept says interactive, make the interaction genuinely work (mouse AND touch).
- Responsive from 360px wide to desktop; no horizontal page scroll. Canvas must handle resize and
  devicePixelRatio. Respect prefers-reduced-motion (reduce/stop non-essential animation).
- Include <!DOCTYPE html>, lang, charset, viewport meta, a good <title>, and a
  <meta name="description">. Add a small unobtrusive link back to "index.html" (styled to fit the
  piece, e.g. a corner "← 100" mark).
- No console errors. Keep performance sane (requestAnimationFrame, cap particle counts).
- Target roughly 200–450 lines per file; depth and polish matter more than length.
- Do NOT touch git, do not edit files other than your 10, do not create extra files.

When done, verify each file loads without JS errors using the preinstalled Playwright
(node, require('playwright'), chromium.launch(), page.on('pageerror'/'console')), and look at a
screenshot of each (deviceScaleFactor 1, saved under your scratch/tmp dir, not the repo) to fix
anything broken or ugly. Report back only: the list of files written and any known issues.
