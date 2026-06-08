"""operai_init.webhook — HTTP receivers for helpdesk providers.

v3.0 ships Richpanel / Gorgias / Zendesk / Intercom. Each provider has its own
payload shape and HMAC signature scheme. This package:

  1. Verifies signatures (fail-closed on mismatch)
  2. Normalizes each provider's payload to a CanonicalTicket
  3. Writes the canonical ticket to /opt/operai/events/<domain>/pending/

The receiver service runs on 127.0.0.1:8788. A Cloudflare Tunnel exposes it
as https://webhook.<brand>.com — the brand configures each helpdesk to POST
to that URL.
"""
__version__ = "3.0.0"
