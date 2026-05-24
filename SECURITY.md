# Security Policy

## Supported Versions

`bitaxe-cockpit` follows a "latest only" support model. Security fixes ship in
the next patch release on the `main` branch; older versions are not
back-patched.

| Version  | Supported          |
| -------- | ------------------ |
| 0.2.x    | :white_check_mark: |
| < 0.2    | :x:                |

If you are pinned to an older version for compatibility reasons, please open a
discussion — we are happy to advise on an upgrade path.

## Threat Model

`bitaxe-cockpit` is a **read-mostly** terminal application that talks to a
local-network Bitaxe device over plain HTTP (AxeOS API) and optionally posts
JSON to a user-configured webhook. It does **not**:

- Store Bitcoin private keys
- Sign transactions
- Open inbound network ports
- Execute remote commands on the Bitaxe
- Run as root or with elevated privileges

The realistic risk surface is therefore:

1. **AxeOS endpoint trust** — the cockpit queries the configured `BITAXE_HOST`
   address. A user pointing at an untrusted device, or a man-in-the-middle on
   the LAN, could feed crafted JSON. We treat AxeOS responses as
   semi-untrusted input and parse defensively.
2. **Webhook payload exposure** — if you configure a webhook
   (`BITAXE_WEBHOOK_URL`), the cockpit sends share/temperature/alert
   metadata. Use HTTPS endpoints and short-lived credentials.
3. **Dependency supply chain** — `textual`, `httpx`, `rich`, and optional
   `zeroconf`. We pin minimum versions in `pyproject.toml` and rely on PyPI's
   advisory database via `pip-audit` in CI.
4. **mDNS discovery (optional)** — when run with `--discover`, the cockpit
   listens for `_axe._tcp` service announcements on the local link. Discovery
   is opt-in and never auto-connects without confirmation.

If your concern falls outside these areas (e.g. ESP32 firmware vulnerabilities,
AxeOS itself, pool stratum protocol), please report upstream to the
[Bitaxe](https://github.com/bitaxeorg) or
[AxeOS](https://github.com/bitaxeorg/ESP-Miner) projects directly.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**
Public exploits of a mining tool — even minor ones — can be weaponized against
solo miners who may not be following the project closely.

### Preferred channel — GitHub Private Vulnerability Reporting

1. Go to the repository's
   [Security tab](https://github.com/mattiacalastri/bitaxe-cockpit/security).
2. Click **Report a vulnerability**.
3. Fill in the advisory form with reproduction steps, affected versions, and
   any proof-of-concept code or logs.

This creates a private GHSA draft that only the maintainer can see.

### Alternative channel — email

If you cannot use GitHub's private reporting (e.g. you are not a GitHub user),
send a plain-text email to:

**agenziacrescita@gmail.com**

Subject line: `[bitaxe-cockpit security] <one-line summary>`

Please include:
- Affected version(s) and OS
- Steps to reproduce
- Impact assessment (what does an attacker gain?)
- Suggested fix or mitigation, if known
- Whether you wish to be credited in the advisory

If you require encryption, request a public key in your first message; we can
exchange a PGP key out-of-band before you send any sensitive details.

## Response Timeline

This is a single-maintainer project run alongside other work. We aim for:

| Stage                          | Target SLA      |
| ------------------------------ | --------------- |
| Acknowledgement of report      | 72 hours        |
| Initial triage + severity vote | 7 days          |
| Fix released (Low / Medium)    | 30 days         |
| Fix released (High / Critical) | 7 days          |
| Public disclosure              | 90 days max     |

If we miss a target, you will hear from us with an updated estimate — silence
is not the answer.

## Coordinated Disclosure

We follow a 90-day coordinated disclosure window by default. We will:

1. Confirm the report and assign a severity.
2. Develop and test a fix in a private branch.
3. Cut a release with the fix.
4. Publish a GitHub Security Advisory (GHSA) crediting you (unless you opt out).
5. Update the `CHANGELOG.md` with a security note.

If a vulnerability is already being exploited in the wild, we will shorten the
disclosure timeline accordingly and may publish a mitigation advisory before a
full fix is available.

## Out of Scope

The following are **not** considered vulnerabilities in `bitaxe-cockpit`:

- Issues in `AxeOS` firmware, `ESP-Miner`, the Bitaxe hardware, or upstream
  Bitcoin/stratum protocols.
- Social-engineering attacks against pool operators or wallet providers.
- Local attacks requiring physical access to a machine running the cockpit
  (terminal session hijacking, root-level keylogging, etc.).
- The pre-configured vendor wallet pattern itself — this is a documented
  *feature class* the cockpit is explicitly designed to surface (see the
  "vendor trap" section of `README.md`). Reports about *specific* vendor units
  shipping with non-disclosed wallets are welcome as discussions, not as
  security issues.

## Thank You

If you take the time to report a vulnerability privately, you are doing the
solo-mining community a real service. We appreciate it.
