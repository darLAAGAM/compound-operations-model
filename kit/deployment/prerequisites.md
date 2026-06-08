# Deployment Prerequisites

This kit is designed for consumer, lifestyle, and retail brands with real operational complexity.

## Best Fit

- Shopify-centered business
- Multiple operational tools already in place
- At least one internal technical operator
- Clear ownership on CS, finance, marketing, merchandising, retail, or people ops
- Willingness to run a staged rollout instead of instant full autonomy

## Not a Fit

- Teams looking for one-click SaaS activation
- Teams without any technical owner
- Companies expecting zero setup, zero debugging, and zero human review
- Very small businesses without stable operational processes yet

## Required Owner

You need one person who can:

- use command line confidently
- provision a VPS or equivalent host
- manage API keys and secrets
- debug broken integrations
- follow a staged rollout with shadow mode and review loops

If you do not have that profile, use the managed option.

## Minimum Technical Stack

- Primary host: Linux VPS with persistent access
- Secondary compute: optional but recommended for multi-agent isolation
- Domain + TLS for MCP endpoint
- Slack and/or email as operating interface
- Access to the systems you want the agents to read or write

## Minimum Access Checklist

- Shopify Admin API
- ERP / finance system access
- Helpdesk access if deploying CS
- Analytics access if deploying marketing
- Inventory / warehouse access if deploying merchandising or ops
- Google Workspace or equivalent for docs / sheets / email workflows

## Security Baseline

Before production, confirm:

- secrets stored outside prompt files
- least-privilege API access per agent
- audit logging enabled
- escalation rules defined
- human review path defined for high-risk actions

## Commercial Expectation

This kit gives you the deployment surface. It does not remove the need for implementation work.
