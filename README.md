# Codex PS5: Payload Manager source

A JSON source for [itsPLK's PS5 Payload Manager](https://github.com/itsPLK/ps5-payload-manager), pointing to the newest published standalone `assistant-service.elf` release from [Portablelle/Codex-PS5](https://github.com/Portablelle/Codex-PS5).

## Add the feed

After pushing these files to a **public** GitHub repository, add this URL through **Settings → Manage Sources → Add Source** in Payload Manager:

`https://raw.githubusercontent.com/JPPurd/codex-ps5-payload-feed/main/payloads.json`

This URL won't work until the GitHub repository and `payloads.json` exist. If you change the repository name or account, change the URL accordingly.

## Automatic updates

GitHub Actions checks upstream releases every six hours, and can be run manually from **Actions → Update Codex PS5 payload feed → Run workflow**. When it finds a new GitHub release containing `assistant-service.elf`, it updates the version, direct download URL and SHA-256 checksum (when GitHub provides one), and commits `payloads.json`. Releases that publish only `codex-portal.tar.gz` are intentionally ignored. If GitHub is down or no suitable ELF exists, the workflow fails rather than clearing the last known working entry.

GitHub Actions must be enabled and permitted to write repository contents. The built-in `GITHUB_TOKEN` is used, so **no personal access token or additional secret is required**.

## Important: this only tracks the ELF

Codex-PS5 also requires its matching ShadowMount application folder (`PPSA99105`). The upstream installation instructions say to update **both components from the same release**, restart the old service, and relaunch the new ELF. This feed cannot install/update the app folder, preserve the correct pairing automatically, or ensure a loaded service is stopped. Use the [Codex-PS5 installation guide](https://github.com/Portablelle/Codex-PS5/blob/main/INSTALL.md) for the full procedure.

The ELF keeps its exact upstream filename, `assistant-service.elf`, so the installed service name does not change. If using an older Payload Manager version, update notifications for constant filenames may not work; use a version with the update-check fix described in [issue #95](https://github.com/itsPLK/ps5-payload-manager/issues/95).

## Files

- `payloads.json`: the actual PS5 Payload Manager catalog.
- `update_payloads.py`: standard-library Python updater.
- `.github/workflows/update-payloads.yml`: scheduled GitHub Actions job.
- `tests/test_update_payloads.py`: updater tests, which run before every scheduled refresh.
