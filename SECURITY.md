# Security Policy

## Reporting a vulnerability

If you find a security issue in the kit, scripts, or any pattern published here, **do not open a public issue.**

Email **hello@usecompai.com** with:

- What you found.
- How to reproduce it.
- The potential impact.

We aim to respond within 72 hours.

## Scope and honest caveats

This repository is an educational implementation portfolio, not a hardened product. Two things are worth saying plainly:

1. **Action control is the hard part.** The most sensitive layer in any deployment is the one that lets agents take real actions (send money, change settings, message customers). The playbook documents the pattern — human-in-the-loop approval, action ledger, reversibility checks, L3 queues — but **a copy of this is only as safe as the approval gates you actually wire in.** Treat every "agent can do X" capability as a risk until you have logging, scoping, and a human approval path around it.

2. **The starter kit is a starting point, not a secure default.** Scripts and templates here assume you will add your own auth, secret management, rate limiting, and least-privilege scoping before pointing them at real systems. Do not run any of this against production data without that work.

## What we do not want

Please never include real credentials, tokens, customer data, or private company information in an issue, PR, or fork you publish. If you spot any in this repo, report it immediately to hello@usecompai.com.
