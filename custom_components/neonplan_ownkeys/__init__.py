"""Register own signing keys for NeonPlan 3D furniture packs.

Adds public keys to neonplan3d's PACK_PUBLIC_KEYS at runtime, so self-signed
packs can be imported without editing packs.py (which HACS updates overwrite).
Keys are managed via the UI (Configure) or, as a legacy fallback, via the
OWN_KEYS dict below plus `neonplan_ownkeys:` in configuration.yaml.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType

from .const import CONF_KEYS, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Legacy fallback: keys used when the integration is enabled via
# `neonplan_ownkeys:` in configuration.yaml instead of a config entry.
OWN_KEYS = {
    "e43284d2e58f": "qWxaLKXfw5jB3mzPiPBCXg4Sg68WkxR+wXS/1xSzswo=",
}


def _packs():
    """Import neonplan3d's packs module (raises if neonplan3d is missing)."""
    from custom_components.neonplan3d import packs

    return packs


def _apply(hass: HomeAssistant, entry_id: str, keys: dict[str, str], packs) -> None:
    """Sync `keys` into PACK_PUBLIC_KEYS, removing keys this entry no longer has."""
    added: set[str] = hass.data.setdefault(DOMAIN, {}).setdefault(entry_id, set())
    for key_id in set(added) - set(keys):
        packs.PACK_PUBLIC_KEYS.pop(key_id, None)
        added.discard(key_id)
    packs.PACK_PUBLIC_KEYS.update(keys)
    added.update(keys)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """YAML fallback: apply the OWN_KEYS above when the domain is configured."""
    if DOMAIN not in config:
        return True
    try:
        _apply(hass, "yaml", dict(OWN_KEYS), _packs())
    except Exception as err:
        _LOGGER.error("neonplan_ownkeys: cannot apply YAML keys to neonplan3d: %r", err)
        return False
    _LOGGER.info("Added %d YAML pack signing key(s) to neonplan3d", len(OWN_KEYS))
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Apply the keys stored in this config entry's options."""
    try:
        packs = _packs()
    except Exception as err:
        raise ConfigEntryNotReady(f"neonplan3d not importable: {err!r}") from err
    _apply(hass, entry.entry_id, dict(entry.options.get(CONF_KEYS, {})), packs)
    entry.async_on_unload(entry.add_update_listener(_options_update))
    _LOGGER.info("neonplan_ownkeys: %d own pack signing key(s) active", len(entry.options.get(CONF_KEYS, {})))
    return True


async def _options_update(hass: HomeAssistant, entry: ConfigEntry) -> None:
    try:
        _apply(hass, entry.entry_id, dict(entry.options.get(CONF_KEYS, {})), _packs())
    except Exception as err:
        _LOGGER.error("neonplan_ownkeys: failed to update keys: %r", err)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove this entry's keys from PACK_PUBLIC_KEYS."""
    added = hass.data.get(DOMAIN, {}).pop(entry.entry_id, set())
    try:
        packs = _packs()
    except Exception:
        return True
    for key_id in added:
        packs.PACK_PUBLIC_KEYS.pop(key_id, None)
    return True
