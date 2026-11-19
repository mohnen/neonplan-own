"""Register own signing keys for NeonPlan 3D furniture packs.

Adds public keys to neonplan3d's PACK_PUBLIC_KEYS at runtime, so self-signed
packs can be imported without editing packs.py (which Marketplace updates overwrite).
Keys are managed via the UI (Configure).

It also keeps configured pack files installed: the pack sources are fetched
periodically and re-imported when missing (e.g. after neonplan3d updates or a
backup restore that skipped them) or when a newer release is published.
"""

from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_KEYS, CONF_PACK_SOURCES, DEFAULT_PACK_SOURCES, DOMAIN

_LOGGER = logging.getLogger(__name__)

_PACK_SYNC_INTERVAL = timedelta(minutes=15)
_HTTP_OK = 200


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


async def _sync_packs(hass: HomeAssistant, entry: ConfigEntry, _now=None) -> None:
    """Install configured pack sources into neonplan3d, once they are missing or outdated."""
    data = hass.data.get("neonplan3d")
    if data is None or not hasattr(data, "async_add_pack"):
        return  # neonplan3d is not set up (yet); the interval retries
    sources = entry.options.get(CONF_PACK_SOURCES)
    if sources is None:
        sources = list(DEFAULT_PACK_SOURCES)
    if not sources:
        return
    packs = _packs()
    from custom_components.neonplan3d import license as lic

    instance = await lic.async_instance_fingerprint(hass)
    session = async_get_clientsession(hass)
    timeout = aiohttp.ClientTimeout(total=30)
    for url in sources:
        url = url.strip()
        if not url:
            continue
        try:
            async with session.get(url, timeout=timeout) as resp:
                if resp.status != _HTTP_OK:
                    _LOGGER.warning("pack source %s: HTTP %s", url, resp.status)
                    continue
                text = await resp.text()
            payload = packs.verify_pack(text, instance=instance)
        except packs.PackError as err:
            _LOGGER.warning("pack source %s: %s", url, err.code)
            continue
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            _LOGGER.warning("pack source %s: %r", url, err)
            continue
        installed = next((p for p in data.packs if p["id"] == payload["id"]), None)
        if installed and int(installed.get("release") or 1) >= int(payload.get("release") or 1):
            continue
        await data.async_add_pack(payload, packs.parts_of(text))
        _LOGGER.info(
            "pack %s release %s installed from %s", payload["id"], payload.get("release") or 1, url
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Apply the keys stored in this config entry's options."""
    try:
        packs = _packs()
    except Exception as err:
        raise ConfigEntryNotReady(f"neonplan3d not importable: {err!r}") from err
    _apply(hass, entry.entry_id, dict(entry.options.get(CONF_KEYS, {})), packs)
    entry.async_on_unload(entry.add_update_listener(_options_update))

    async def _tick(now) -> None:
        await _sync_packs(hass, entry, now)

    entry.async_on_unload(async_track_time_interval(hass, _tick, _PACK_SYNC_INTERVAL))
    hass.async_create_task(_sync_packs(hass, entry))
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
