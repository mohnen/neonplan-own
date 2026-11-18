"""Constants for the NeonPlan own pack keys integration."""

DOMAIN = "neonplan_ownkeys"
CONF_KEYS = "keys"
KEY_ID_RE = r"^[0-9a-f]{12}$"

# Keys a new config entry is seeded with (key id -> raw Ed25519 public key,
# base64, as printed by `python tools/fp3dpack.py keygen <keyfile>`).
DEFAULT_KEYS = {
    "e43284d2e58f": "qWxaLKXfw5jB3mzPiPBCXg4Sg68WkxR+wXS/1xSzswo=",
}
