"""Per-provider payload → CanonicalTicket normalizers.

Each module exposes:
  normalize(payload: dict) -> dict   # the CanonicalTicket
  source_ticket_id(payload: dict) -> str

The CanonicalTicket schema is stable and fed directly to the factory runtime.
Fields unknown to the source are left unset; brain_lookup + workflow hooks
fill them later.
"""
