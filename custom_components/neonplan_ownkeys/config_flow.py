"""Config and options flow for NeonPlan own pack keys."""

from __future__ import annotations

import base64
import hashlib
import logging
from pathlib import Path
import re
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.helpers import selector

from .const import CONF_KEYS, DEFAULT_KEYS, DOMAIN, KEY_ID_RE

_LOGGER = logging.getLogger(__name__)


def _valid_public_key(value: str) -> bool:
    """A raw Ed25519 public key is 32 bytes, base64-encoded."""
    try:
        return len(base64.b64decode(value, validate=True)) == 32
    except Exception:
        return False


def _valid_key_id(value: str) -> bool:
    return bool(re.fullmatch(KEY_ID_RE, value))


class NeonplanOwnkeysConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up the integration once; keys are managed via Configure."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user")
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="NeonPlan own pack keys", data={}, options={CONF_KEYS: dict(DEFAULT_KEYS)}
        )

    @staticmethod
    def async_get_options_flow(config_entry) -> OptionsFlow:
        return NeonplanOwnkeysOptionsFlow()


class NeonplanOwnkeysOptionsFlow(OptionsFlow):
    """Add, generate, update and delete pack signing keys."""

    def _keys(self) -> dict[str, str]:
        return dict(self.config_entry.options.get(CONF_KEYS, {}))

    def _save(self, keys: dict[str, str]) -> ConfigFlowResult:
        return self.async_create_entry(data={CONF_KEYS: keys})

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        # menu_options as a dict shows these labels directly, without translations
        menu = {"add": "Add a public key", "generate": "Generate a new signing key"}
        if self._keys():
            menu["update"] = "Update a key"
            menu["delete"] = "Delete keys"
        return self.async_show_menu(step_id="init", menu_options=menu)

    # -- add an existing public key -------------------------------------------------

    async def async_step_add(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            key_id = user_input["key_id"].strip()
            public = user_input["public_key"].strip()
            if not _valid_key_id(key_id):
                errors["key_id"] = "invalid_key_id"
            elif not _valid_public_key(public):
                errors["public_key"] = "invalid_public_key"
            else:
                keys = self._keys()
                keys[key_id] = public
                return self._save(keys)
        return self.async_show_form(
            step_id="add",
            data_schema=vol.Schema(
                {vol.Required("key_id"): str, vol.Required("public_key"): str}
            ),
            errors=errors,
        )

    # -- generate a new Ed25519 signing key -----------------------------------------

    def _write_key(self, pem: bytes) -> None:
        self._key_dir.mkdir(parents=True, exist_ok=True)
        self._pem_path.write_bytes(pem)

    async def async_step_generate(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        private = Ed25519PrivateKey.generate()
        raw_public = private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        self._key_id = hashlib.sha256(raw_public).hexdigest()[:12]
        self._public = base64.b64encode(raw_public).decode()
        pem = private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        self._key_dir = Path(self.hass.config.path("neonplan_ownkeys"))
        self._pem_path = self._key_dir / f"{self._key_id}.pem"
        await self.hass.async_add_executor_job(self._write_key, pem)
        keys = self._keys()
        keys[self._key_id] = self._public
        self._keys_after = keys
        return await self.async_step_generated()

    async def async_step_generated(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self._save(self._keys_after)
        return self.async_show_form(
            step_id="generated",
            description_placeholders={
                "key_id": self._key_id,
                "public_key": self._public,
                "path": str(self._pem_path),
            },
        )

    # -- update an existing key ------------------------------------------------------

    async def async_step_update(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        keys = self._keys()
        if not keys:
            return self.async_abort(reason="no_keys")
        errors: dict[str, str] = {}
        if user_input is not None:
            public = user_input["public_key"].strip()
            if not _valid_public_key(public):
                errors["public_key"] = "invalid_public_key"
            else:
                keys[user_input["key_id"]] = public
                return self._save(keys)
        return self.async_show_form(
            step_id="update",
            data_schema=vol.Schema(
                {
                    vol.Required("key_id"): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=list(keys), mode="dropdown")
                    ),
                    vol.Required("public_key"): str,
                }
            ),
            errors=errors,
        )

    # -- delete keys ------------------------------------------------------------------

    async def async_step_delete(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        keys = self._keys()
        if not keys:
            return self.async_abort(reason="no_keys")
        if user_input is not None:
            for key_id in user_input["key_ids"]:
                keys.pop(key_id, None)
            return self._save(keys)
        return self.async_show_form(
            step_id="delete",
            data_schema=vol.Schema(
                {
                    vol.Required("key_ids"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(keys), mode="list", multiple=True
                        )
                    )
                }
            ),
        )
