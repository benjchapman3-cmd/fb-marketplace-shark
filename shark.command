#!/bin/bash
# shark.command — one-command Shark launcher (double-click on macOS).
# Opens the hosted Deal CRM and prints the scan trigger.
CRM="https://benjchapman3-cmd.github.io/fb-marketplace-shark/"
open "$CRM"
cat <<'EOF'
🦈  MARKETPLACE SHARK
────────────────────────────────
Deal CRM opened in your browser.

To scan, in a Claude Code session say:
  • "run the shark"              (scout only — no messages)
  • "run the shark" + "go autonomous"  (negotiate within mandate)
  • "launch the shark"           (NYC launch checklist)

CRM: https://benjchapman3-cmd.github.io/fb-marketplace-shark/
EOF
