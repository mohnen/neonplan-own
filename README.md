# NeonPlan own pack keys

Home Assistant custom integration that registers **your own Ed25519 public keys**
in [NeonPlan 3D](https://github.com/Mastershort/neonplan3d), so furniture packs
you sign yourself (with `tools/fp3dpack.py` from the neonplan3d repository) can
be imported — without patching `packs.py`, which every NeonPlan update would
overwrite.

## Install via Marketplace

1. Marketplace → **Add repository** → paste
   `https://github.com/mohnen/neonplan-own`, type **Integration**
2. Install **NeonPlan own pack keys**
3. Restart Home Assistant
4. Settings → Devices & services → **Add integration** → "NeonPlan own pack keys"

Requires NeonPlan 3D to be installed. A new entry is seeded with the default
key in `const.py` (`DEFAULT_KEYS`) — delete it via Configure if you don't need it.

## Managing keys

Settings → Devices & services → NeonPlan own pack keys → **Configure**:

- **Add a public key** — paste the key ID and base64 public key printed by
  `python tools/fp3dpack.py keygen keyfile.pem`
- **Generate a new signing key** — creates an Ed25519 keypair, registers the
  public key and saves the private key to
  `config/neonplan_ownkeys/<key_id>.pem`
- **Update a key** — replace the public key of an existing key ID
- **Delete keys** — remove keys; changes apply immediately, no restart needed
