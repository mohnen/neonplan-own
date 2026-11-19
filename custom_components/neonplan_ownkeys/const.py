"""Constants for the NeonPlan own pack keys integration."""

DOMAIN = "neonplan_ownkeys"
CONF_KEYS = "keys"
CONF_PACK_SOURCES = "pack_sources"
KEY_ID_RE = r"^[0-9a-f]{12}$"

# Keys a new config entry is seeded with (key id -> raw Ed25519 public key,
# base64, as printed by `python tools/fp3dpack.py keygen <keyfile>`).
DEFAULT_KEYS = {
    "e43284d2e58f": "qWxaLKXfw5jB3mzPiPBCXg4Sg68WkxR+wXS/1xSzswo=",
}

# Pack files auto-installed (and kept current) in neonplan3d.
DEFAULT_PACK_SOURCES = (
    "https://raw.githubusercontent.com/mohnen/neonplan-own/master/packs/ikea.fp3dpack",
    "https://raw.githubusercontent.com/mohnen/neonplan-own/master/packs/jysk.fp3dpack",
)
