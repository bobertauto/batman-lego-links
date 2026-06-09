#!/bin/bash
# One-step deploy of the affiliate bio page to GitHub Pages.
# PREREQ (you, once): gh auth login   (choose GitHub.com → HTTPS → browser)
# Then run: ./deploy.sh
set -e
cd "$(dirname "$0")"
REPO="batman-lego-links"
git add -A && git commit -m "affiliate bio page" -q || true
gh repo create "$REPO" --public --source=. --remote=origin --push
gh api -X POST "repos/{owner}/$REPO/pages" -f "source[branch]=main" -f "source[path]=/" 2>/dev/null || \
  echo "If Pages didn't auto-enable: GitHub repo → Settings → Pages → Branch: main /(root) → Save"
echo "Live in ~1 min at: https://<your-gh-username>.github.io/$REPO/"
