# Thermine-raspi — ToDo

Consolidated list of bugs, improvements and release tips raised during the code-review session. Items are grouped by project area and prioritized.

Legend:
- 🔴 **Critical** — broken code, prevents the feature from working
- 🟠 **High** — correctness/safety issue in normal multi-miner operation
- 🟡 **Medium** — robustness, maintainability
- 🔵 **Low** — cosmetic, dead code, typos
- 🟢 **Release** — packaging / distribution work

---

## 1. `Thermostat/Controller/Miner/` — Miner integrations

### `miner_whatsminer.py`  🔴
The whole module is currently non-importable. Fix in this order:

- [ ] **L17** — `return = rsp_info` is a Python SyntaxError. Replace with `return rsp_info`.
- [ ] **L113** — Invalid return annotation `-> WhatsminerAPIv3, WhatsminerTCP, str`. Use `-> Tuple[WhatsminerAPIv3, WhatsminerTCP, str]` (and import `Tuple` from `typing`).
- [ ] **L12, L29, L41, L54, L67, L79, L87, L145** — Calls to bare `getSession(jObj)` will raise `NameError`. Use `MinerWhatsminer.getSession(jObj)`.
- [ ] **L12, L29, L41, L54, L67, L79, L87, L145** — `getSession` returns 3 values (`api, tcp, salt`) but most callers unpack 2. Align unpack with definition.
- [ ] **L96–L98** — References to `whatsminer_api` / `whatsminer_tcp` are undefined locals (copy-paste leftover from `getSession`). Use the local `api` / `tcp` returned by `getSession`.
- [ ] **L195, L202** — Calls to `MinerWhatsminer.postResume` / `postPause` that do not exist. Replace with `MinerWhatsminer.resume` / `MinerWhatsminer.pause`.
- [ ] **L175–L182** — `rsp_info` is referenced but never assigned in that scope. Issue the `get.miner.status / summary` request first and assign it.
- [ ] **`MinerUtils.CompatibleFirmware` enum and `MinerUtils.getMinerClass()`** ([miner_utils.py:268](Thermostat/Controller/Miner/miner_utils.py:268), [:328](Thermostat/Controller/Miner/miner_utils.py:328)) — Whatsminer is not registered. Add `whatsminer = 'whatsminer'` and the dispatch branch returning `MinerWhatsminer`.
- [ ] Register `MinerWhatsminer` in [`Controller/Miner/__init__.py`](Thermostat/Controller/Miner/__init__.py).

### `miner.py`  🔴
- [ ] **L246, L253** — References to undefined `tCurrent` inside `Miner.minerThermalControl`. The local variable is named `temp`. Replace `tCurrent` with `temp` in both log messages (or rename `temp` to `tCurrent` for consistency with the per-firmware methods).

### `miner_luxor.py`  🔴
- [ ] **L163, L166** — `pause` and `resume` are decorated `@classmethod` but defined as `def pause(jObj):` / `def resume(jObj):` — missing `cls` first arg. Calls will misbind. Add `cls` to both signatures.

### `miner_vnish.py`  🟠 (multi-miner correctness)
- [ ] **L8** — `MinerVnish.TOKEN = ""` is a **class-level** attribute. With N Vnish miners that have different passwords/IPs, the first miner's token is reused for all of them → cross-miner control or auth failures.
  - Fix: store tokens in a per-UUID dict guarded by a lock, e.g. `_tokens: Dict[str, str] = {}` keyed by `jObj['uuid']`.

### `miner_braiins_s9.py`  🟠 (multi-miner correctness)
- [ ] **L24, L25** — `lockServiceBosminer` and `lockFileBosminerToml` are class-level locks. An SSH operation against miner A unnecessarily blocks operations against miner B.
  - Fix: per-UUID (or per-IP) locks held in a dict guarded by a small registry lock.

### `miner_utils.py`  🟡
- [ ] **`dataHashrateLastJson` (L143)** — does not guard against `None` returned by `dataHashrateLast`; will raise `TypeError` on a fresh miner with no data file yet. Mirror the `None` check from `dataTemperatureSensorLastJson`.
- [ ] **`dataCurrentStatus` (L66)** — typo `'hasrate'` / `'hasrate_old'` (missing `h`). Pick a single key (`'hashrate'`) and update both writes and any consumer.
- [ ] **`binaryReadingFileStr` (L17)** — log line uses `path` which is not in scope. Pass `fileName` (the parameter) to the log message.

---

## 2. `Thermostat/Controller/Http/` — HTTP control plane

### Security  🟠
- [ ] **`web_service.py` L18–L19** — Hard-coded `admin / senha123` credentials shipped in source. Every installation gets the same password.
  - Fix: on first boot, generate a random username/password, persist it in `~/Documents/heater_control/config/thermine_config.json` (or `/etc/thermine/`), and print it once to the log so the operator can capture it.
- [ ] No TLS on the local HTTP service. Acceptable on a trusted LAN, but document it; consider exposing an option to terminate TLS via a reverse proxy in the systemd unit.

### Robustness  🟡
- [ ] Replace `http.server.BaseHTTPRequestHandler` + `socketserver.TCPServer` with a small WSGI app served by `waitress` (single pure-Python dependency, threaded, production-grade). Keeps the synchronous style; removes hand-rolled auth/header parsing bugs and gives proper request lifecycle.
- [ ] **`web_service_handler.py` L84** — content-type typo `'application/jsonn'` on `/Miner/Hashrate/Last`.
- [ ] **`web_service_handler.py` L36** — leftover `print('1')` in `handle_del`.

---

## 3. `Thermostat/Controller/utils.py` — Shared utilities

### `Utils.PubSub`  🟠
- [ ] The subscriber dictionary is mutated from multiple threads without a lock — race between `subscribe` / `unsubscribe` / `publish`.
- [ ] `publish` invokes callbacks **synchronously on the publisher's thread**. A scheduled `MinerService` job can call `MinerService.dataHasChanged → self.stop() → BackgroundScheduler.shutdown()` from inside the scheduler's own worker → deadlock risk.
  - Fix: guard `subscribers` with a lock, and dispatch callbacks to a dedicated worker thread (or a small `ThreadPoolExecutor`) so handlers never run on the publishing thread.

### Other  🟡
- [ ] **L41** — Two functions both named `dataClassListToJson` with different signatures; the second silently overwrites the first. Rename one (e.g. `jsonToDataClassList`).
- [ ] **L354** — `Utils.grpcChannelSecure(aip)` is called with one argument but the function requires `(aip, token)`. Dead branch today (only HTTP gRPC is used), but will crash if HTTPS is ever turned on.
- [ ] **L527** — `ssh.close;` is a no-op (missing `()`). Should be `ssh.close()`.
- [ ] gRPC channels are created and closed per call. For miners polled every 5 s, cache one channel per miner UUID and reuse it.

---

## 4. `Thermostat/Controller/w1thermsensor_utils.py`

- [ ] **L85** — Typo `Exceptionprint("getTemperature1")` — invalid expression on the same line as a fallback assignment. The line is dead until the import error path is hit, then it crashes. Split into proper statements and remove the stray `print`.
- [ ] **L57** `loadW1Modules` calls `sudo modprobe ...` via `os.system`. In a packaged install the service should already run with required modules loaded by the systemd unit (`ExecStartPre=/sbin/modprobe ...`) or by `dtoverlay=w1-gpio` at boot — drop the runtime `sudo` calls.

---

## 5. `Thermostat/Controller/Miner/miner_service.py` — Scheduling

### Architecture cleanup  🟡
The four cleanups discussed, in priority order:

- [ ] **One global scheduler, many jobs.** Today every `MinerService` instance creates two `BackgroundScheduler`s (= 2 thread pools per miner). With 10 miners that's 20 schedulers. Refactor to a single module-level `BackgroundScheduler` with a sized `ThreadPoolExecutor` (~8 workers) and add per-miner jobs (`id=f"readData_{uuid}"`, `id=f"thermal_{uuid}"`) to it. `MinerService.start()` adds jobs; `stop()` removes them. Single shutdown on process exit.
- [ ] **Per-instance state, not class-level.** Move `MinerVnish.TOKEN` and `MinerBraiinsS9` locks to per-UUID containers (see items in §1).
- [ ] **Thread-safe PubSub + off-thread dispatch.** See §3.
- [ ] **Replace `http.server` with `waitress`.** See §2.

### Dead code  🔵
- [ ] After centralizing the thermal logic in `Miner.minerThermalControl`, the per-firmware `minerThermalControl` methods are no longer called. Remove them from `MinerBraiinsV1`, `MinerBraiinsS9`, `MinerLuxor`, `MinerVnish`, `MinerWhatsminer` (and from the `MinerBase` contract) once the centralized path is verified end-to-end.

---

## 6. `Thermostat/Controller/Miner/Braiins_1.4.0/`  🔵

- [ ] Kept intentionally as a rollback snapshot. Add a top-of-file `README.md` note clarifying that, so future contributors don't try to wire it in. Exclude the folder from the PyInstaller build (see §7) to avoid bloating the binary.

---

## 7. Release / Packaging — Option B (`.deb` wrapping a PyInstaller binary)  🟢

Target: Raspberry Pi OS (Bookworm first, Bullseye if needed). One `.deb` per Pi-OS major version, per arch (`armhf` / `arm64`).

### Build pipeline
- [ ] Add a `build/` (or `packaging/`) folder with:
  - `build/pyinstaller.spec` — entry `Thermostat/main.py`, hidden imports for `grpc`, `paramiko`, `w1thermsensor`, `apscheduler`, `Crypto` (PyCryptodome). Exclude `Braiins_1.4.0/`.
  - `build/debian/` — control file, `postinst`, `prerm`, `postrm`, systemd unit, default config.
  - `build/build.sh` — runs PyInstaller, then `fpm` (or `dpkg-deb`) to wrap the resulting binary into a `.deb`.
- [ ] Set up CI (GitHub Actions) using ARM runners (or `docker buildx` + `qemu-user-static`) so contributors don't need a physical Pi to produce artifacts.

### `.deb` contents
- [ ] **Binary**: `/usr/bin/thermine-raspi` (the PyInstaller one-file output).
- [ ] **systemd unit**: `/lib/systemd/system/thermine-raspi.service`
  - `Restart=always`, `User=thermine`, `Group=thermine`, `RuntimeDirectory=thermine`.
  - `ExecStartPre=/sbin/modprobe w1-gpio` and `w1-therm` (so the 1-Wire sensor works without manual setup).
- [ ] **Default config**: `/etc/thermine/thermine_config.json` (empty/template). Move data dir from `~/Documents/heater_control/` to `/var/lib/thermine/` for a system service.
- [ ] **postinst**:
  - Create `thermine` system user/group.
  - Create `/var/lib/thermine/{config,data}` with correct ownership.
  - Append `dtoverlay=w1-gpio` to `/boot/config.txt` if missing (idempotent, with a backup).
  - **Generate a random HTTP user/password on first install**, write to `/etc/thermine/credentials.json` (mode 0600, owned by `thermine`), and `echo` it once to stdout so `apt` shows it during install.
  - `systemctl daemon-reload && systemctl enable --now thermine-raspi`.
- [ ] **prerm / postrm**: stop and disable the service; on `purge`, remove `/var/lib/thermine` and `/etc/thermine` (but **not** the `dtoverlay` line — that's shared system config).

### Code changes required to support packaging
- [ ] Make data/config paths configurable via env var (e.g. `THERMINE_DATA_DIR`, `THERMINE_CONFIG_DIR`) with the current `~/Documents/heater_control/` layout as the default for dev. The systemd unit sets them to `/var/lib/thermine` and `/etc/thermine`.
- [ ] Read HTTP credentials from `/etc/thermine/credentials.json` instead of the hard-coded constants.
- [ ] Have `main.py` accept `--config-dir` / `--data-dir` flags as an alternative to env vars (handy for local testing).

### Documentation
- [ ] Update [README.md](README.md) with a "Install" section that is just:
  ```
  sudo apt install ./thermine-raspi_<version>_<arch>.deb
  ```
  and note that the generated credentials are printed during install and stored in `/etc/thermine/credentials.json`.
- [ ] Move the current Python-from-source build instructions into a `docs/DEVELOPMENT.md` — they're for contributors, not end users.

---

## 8. Suggested order of attack

1. Fix the 🔴 critical bugs (§1 Whatsminer, `miner.py`, `miner_luxor.py`) — code currently can't run those paths.
2. Fix the 🟠 multi-miner correctness bugs (`MinerVnish.TOKEN`, S9 locks, `PubSub` thread-safety + off-thread dispatch, hard-coded credentials).
3. Architecture cleanup §5 (one scheduler; remove dead per-firmware thermal methods).
4. Replace HTTP server with `waitress` (§2).
5. Mop up 🟡 / 🔵 items.
6. Stand up the packaging pipeline (§7) once the runtime is stable.
