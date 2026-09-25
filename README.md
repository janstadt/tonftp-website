# TONFTP LLC Marketing Website

Static, zero-dependency marketing site for **TONFTP LLC**, deployed to GitHub
Pages. It presents TONFTP LLC as the owner and operator of `tonftp.com` and as
an independent software development company focused on web and native
applications.

**Live URL (target):** `https://www.tonftp.com/`
GitHub Pages URL: `https://janstadt.github.io/tonftp-website/`

This repo follows the same pattern as
[`cabin-clarity-website`](../cabin-clarity-website): plain static files at the
repo root, published by a GitHub Actions workflow, with the custom domain
declared via a `CNAME` file.

## Why plain HTML/CSS/JS (no Astro / Eleventy / build step)?

This is a single-page marketing site. A static-site generator would add
hundreds of npm dependencies and a build pipeline for zero benefit here. Plain
files mean:

- **Fastest possible load** — no framework runtime, two files to download
- **Trivially maintainable** — edit HTML text directly, no toolchain
- **Instant deploys** — GitHub Actions just uploads the folder

If the site ever grows to many pages or needs templating, migrate to
[Astro](https://astro.build) — the design system in `style.css` ports over
directly.

## Files

```
tonftp-website/
├── index.html          # All page content & sections
├── style.css           # Design system (navy/cyan palette, see below)
├── script.js           # Shared footer + reveal-on-scroll (IntersectionObserver)
├── assets/
│   ├── icon.png        # 512px mark (brand, apple-touch-icon, JSON-LD logo)
│   ├── favicon.png     # 64px favicon
│   └── og.png          # 1200x630 Open Graph / Twitter card image
├── tools/
│   └── make-icons.py   # Regenerates assets/*.png (Pillow, deterministic)
├── CNAME               # www.tonftp.com — tells GitHub Pages the custom domain
├── robots.txt
├── sitemap.xml
├── llms.txt            # Plain-text summary for AI crawlers
└── .github/workflows/website.yml
```

## Design system

Shared palette with the CabinClarity site:

| Token   | Hex       | Use                          |
|---------|-----------|------------------------------|
| navy    | `#06182A` | Page background              |
| brand   | `#04639A` | Primary blue (gradients, CTAs) |
| cyan    | `#3EC6F0` | Accent, gradients, links     |
| ice     | `#BFE9FF` | Subtle text, borders         |

Style notes: dark immersive hero with animated gradient orbs and a blueprint
grid, glassmorphism cards, a bento services grid, a CSS-only code window
(decorative), IntersectionObserver scroll reveals with stagger, and full
`prefers-reduced-motion` support. No images are required to render the layout.

Retheme by editing the `:root` variables at the top of `style.css`.

### Regenerating the images

```bash
python3 tools/make-icons.py   # requires Pillow → icon.png, favicon.png, og.png
```

## SEO

Already in place:

- **Titles & snippets** — 54-char `<title>`, 141-char meta description (both
  inside Google's display limits), `canonical`, `max-image-preview:large`
- **Social cards** — Open Graph + Twitter `summary_large_image` with a real
  1200×630 `og.png` (not a square icon crop) and alt text on every image
- **Structured data** — one JSON-LD `@graph` with `Organization`
  (`legalName: TONFTP LLC`, `logo`, `email`, `knowsAbout`, `contactPoint`)
  linked to a `WebSite` node via `publisher` `@id`, so Google can resolve
  "TONFTP LLC" as an entity rather than a keyword
- **Crawlability** — `robots.txt` + `sitemap.xml` + `llms.txt`, one `<h1>`,
  no heading-level skips, descriptive anchor text, semantic `nav`/`main`/
  `footer` landmarks
- **Core Web Vitals** — no external fonts (system stack), no layout images, one
  stylesheet, ~2 KB of JS, `no-js` fallback so content is never JS-gated

Deliberately **not** claimed: no `sameAs` social profiles, no business address
or telephone in structured data, and no `LocalBusiness` markup — those require
facts the LLC has not published. Add them when they exist; inventing them hurts
more than it helps.

## Deploying

Automatic: push to `main` → `.github/workflows/website.yml` stages the site into
`_site/` and publishes it (no build step). Staging keeps `README.md` and
`tools/` off the public web root.

**Two one-time prerequisites — the build fails without either:**

1. **The repo must be public.** GitHub Pages is unavailable for private repos
   on the free plan; the Pages API returns `422 Your current plan does not
   support GitHub Pages for this repository`, which surfaces in Actions as
   `HttpError: Not Found` from `configure-pages`.
2. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
   Equivalent via CLI:
   ```bash
   gh api -X POST repos/janstadt/tonftp-website/pages -f build_type=workflow
   ```

  (Do not bother with `enablement: true` on `configure-pages`: it requires a
  token other than the default `GITHUB_TOKEN`, so it cannot self-heal.)

Manual trigger: Actions tab → "website" → Run workflow.

### Local preview

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

## Custom domain — DNS setup

`tonftp.com` currently hosts the homelab's own subdomains (e.g.
`ha.tonftp.com`, `plex.tonftp.com`) via Cloudflare. **Only the apex and `www`
records change.** Do not touch the existing subdomain records, wildcards, or the
AdGuard Home / Unbound split-horizon config — the homelab depends on those.

> ⚠️ This is the one place where a mistake is user-visible. The site lives on
> the **apex/`www` only**; every service subdomain must keep resolving to the
> homelab as it does today.

1. **Repo Settings → Pages → Custom domain** — enter `www.tonftp.com` and save
   (the `CNAME` file already contains it). GitHub will display a
   `_github-pages-challenge-janstadt` TXT record to add for verification.
2. **Cloudflare DNS** (grey cloud / DNS-only for these two, so GitHub can
   issue the Let's Encrypt certificate):
   - `A` `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`,
     `185.199.111.153`
   - `CNAME` `www` → `janstadt.github.io`
   - `TXT` `_github-pages-challenge-janstadt` → value shown by GitHub
3. **Wait for DNS propagation**, then tick **Enforce HTTPS** in Pages settings.
   GitHub provisions the certificate automatically; apex requests redirect to
   `www.tonftp.com`.

Internal (LAN) resolution is unaffected: OPNsense Unbound forwards the
`tonftp.com` zone to AdGuard Home, which answers from local rewrites. If you
also want the marketing site reachable on the LAN under a non-public name, add
a rewrite instead of changing the public apex.

## Editing content

- **Copy / sections** → `index.html` (each section has an HTML comment banner)
- **Colors / spacing / fonts** → `:root` variables in `style.css`
- **Footer links + copyright line** → `FOOTER_NOTE` in `script.js`
- **Crawler / SEO files** → `robots.txt`, `sitemap.xml`, `llms.txt`

## Before public launch — TODOs

- [ ] **Confirm the contact email.** Currently `hello@tonftp.com` everywhere
      (`index.html` ×3, `script.js`, `llms.txt`, structured data in
      `index.html`). Swap for the real address once decided.
- [ ] Confirm the **CabinClarity** link may be referenced publicly as work.
- [ ] Optional: add a registered business address / phone to the "The entity"
      card in `index.html` if the LLC wants them public.
- [ ] Optional: add a `privacy.html` (the site sets no cookies and collects
      nothing today, so one is not strictly required).
- [ ] Update `<lastmod>` in `sitemap.xml` when content changes.
