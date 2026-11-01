---
title: Release safety notes
---

# Release safety notes

Every change to `main` (including the bot's activity-log commits) goes through the **Release site** workflow:

1. **build**: Jekyll builds the site and stamps the commit SHA into `version.txt`.
2. **validate** (the gate): `scripts/check_site.py` checks the exact artifact that would be deployed: README markers present, homepage renders *Recent activity*, `version.txt` matches the commit, and every internal link points to a file that exists.
3. **deploy**: runs only if the gate passed.
4. **smoke test**: the live URL must serve this exact version, not just HTTP 200.

If the gate fails, nothing is deployed and visitors keep the last good version.

[Back to the homepage](./)
