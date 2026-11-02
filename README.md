# Ai00 for 4D

Run the [Ai00 RWKV inference server](https://github.com/Ai00-X/ai00_server)
from 4D 20+ on Apple Silicon, Intel macOS, or Windows x64. RWKV keeps a
fixed-size recurrent inference state rather than a growing transformer KV
cache; this is not a guarantee of unlimited effective model context.

## Upstream version

As checked on **2026-11-02**, the latest upstream release is
**[v0.7.1](https://github.com/Ai00-X/ai00_server/releases/tag/v0.7.1)**,
published **2026-06-09**. Both that tag and upstream `main` HEAD resolve to
**`54ddbd6818499b11bfd0469d2ea59577d8076c92`** (commit date 2026-06-09).
Builds use this exact commit, not a moving branch or downloaded server binary.
The upstream Cargo package still declares **0.6.2**: `ai00-server --version`
reports that package version, **not** the v0.7.1 release tag.

[upstream.json](https://github.com/miyako/ai00/blob/main/upstream.json)
records the source revision, Rust toolchain, lockfile and runtime asset hashes.
Default upstream features, including optional ONNX embeddings, are compiled.
The 4D wrapper configures RWKV chat/completions, not an embedding model.

## Install the 4D component

Download a component from this repository's
[Releases](https://github.com/miyako/ai00/releases), unzip `Ai00.zip`, and
install `Ai00.4dbase` in your application's `Components` folder. Releases
predating this source-build update contain the old bundled server binaries.
The 4D project also declares `miyako/event`, `miyako/workers`, and
`miyako/tcp` in `Project/Sources/dependencies.json`. Make these components
available to your host project using 4D's component manager (or their
released `.4dbase` bundles); the custom callback example uses `cs.event`.

New component releases require successful builds for **all three** targets:

| Host | Rust target | Component executable |
|---|---|---|
| Apple Silicon macOS | `aarch64-apple-darwin` | `Resources/bin/macOS/ai00-server` |
| Intel macOS | `x86_64-apple-darwin` | `Resources/bin/macOS/ai00-server-x86_64` |
| Windows x64 | `x86_64-pc-windows-msvc` | `Resources/bin/Windows/ai00-server.exe` |

Use macOS 11+ (also subject to your 4D version's requirements) or Windows
with current graphics drivers and the Visual C++ x64 runtime. Inference
needs a WebGPU-compatible GPU/backend (Metal on macOS, Vulkan/DX12 where
available on Windows) and enough memory for the chosen model. No CUDA or
Python is required for server inference. A CPU embedding option does not
make RWKV inference a CPU-only backend.

The wrapper does not support Linux or Windows ARM. Upstream also publishes
Linux x64, but this repository's 4D launcher only selects macOS and Windows.
CI failures on any retained target block component publishing; targets are
not silently omitted.

## Build the server from source

Install Git with **Git LFS**, Python **3.9+**, Rust/rustup, and native build
tools: Xcode Command Line Tools on macOS, or Visual Studio C++ Build Tools
and the Windows SDK on Windows. The commands below run in the repository
root. Network access is required for upstream source/LFS, crates and the
default ONNX Runtime build dependency.

```sh
git clone https://github.com/miyako/ai00.git
cd ai00
git lfs install
rustup toolchain install 1.91.0 --profile minimal
rustup target add --toolchain 1.91.0 aarch64-apple-darwin
python3 scripts/build-server.py --target aarch64-apple-darwin
```

Use `python` on Windows and substitute `x86_64-pc-windows-msvc`; Intel Mac
users substitute `x86_64-apple-darwin`. These are **native build and CLI
smoke-test commands**, not a cross-compilation recipe. The script runs
`cargo +1.91.0 build --locked --release --package ai00-server --target ...`
with upstream default features. Upstream's manifest minimum (1.76) and
README badge (1.78) are not reliable minimums for its newer locked
dependencies; this repository pins a newer compiler.

The upstream workspace contains `crates/ai00-server` and `crates/ai00-core`,
with the checked-in `crates/ort-patch` override. The `hf-hub` Git dependency
is resolved by upstream's `Cargo.lock`. There are no Git submodules; the
WebUI ZIP is a Git LFS asset and must be fetched as real content.

The checkout is `.build/ai00_server`; the output is `dist/<target>/`, a
**Resources overlay**, containing the CLI, tokenizer, WebUI, upstream
license, target-specific provenance/checksums and Windows ONNX Runtime DLL.
Git LFS pointers, a dirty/wrong source checkout, altered assets, failed
builds, and failed `--help`/`--version` checks are fatal.

For local development, copy the overlay into `Ai00/Resources` before opening
the 4D project, for example on Apple Silicon:

```sh
cp -R dist/aarch64-apple-darwin/. Ai00/Resources/
```

Server executables are generated/ignored, not checked into Git. A fresh
source checkout must be built before launching the component. Legacy native
**converter** executables remain separately bundled at
`Resources/bin/macOS/converter` (universal) and
`Resources/bin/Windows/converter.exe`. Their original source revision is
unrecorded; they are **not** rebuilt or claimed to match v0.7.1. Upstream's
`crates/converter` is currently excluded from its workspace, so the README's
`cargo run --package converter` command is not valid at this revision.

### CI and component publishing

The **Build server from source** workflow builds and smoke-tests on native
Apple Silicon macOS, Intel macOS and Windows x64 runners. It uploads
`server-<target>` artifacts (seven-day retention), not standalone end-user
distributions. Each contains the Resources overlay described above.

Both hosted and self-hosted **Publish** paths depend on those builds,
set the package version on a clean checkout before staging generated files
(`npm version` requires a clean working tree), then download/merge all three
overlays into `Ai00/Resources` and verify their
provenance and file checksums before invoking the existing tool4d component
build, Apple signing/notarization and release actions. They also explicitly
restore the existing declared `event`, `workers`, and `tcp` dependencies
into `Ai00/Components`, because the compiler action discovers local
components rather than resolving `dependencies.json` itself. This fixes a
pre-existing clean-checkout setup gap. The declarations still use `latest`;
resolved tags and archive hashes are recorded in
`Resources/upstream/components.json` (separate from the immutable server pin).
The compiled `.4DZ` and copied server resources are checked again before
signing, so a compiler helper that exits zero after reporting failure cannot
publish an incomplete component. Provenance checksums describe the
pre-signing build outputs; Apple code signing subsequently changes binaries.
Self-hosted mode
selects the component packaging host; server builds still use hosted native
runners. Component publishing needs the existing 4D tool/dependencies and
Apple signing/notarization secrets; Python 3.9+ is also needed on the
self-hosted packaging runner, along with `gh` and macOS `ditto` for restoring
the declared components. `Ai00.zip`/`Ai00.dmg` retain the existing
component release format.

## Use from 4D

Create the shared component instance in *On Startup*:

```4d
var $Ai00 : cs.Ai00.Ai00
$Ai00:=cs.Ai00.Ai00.new()
```

The default model is
`rwkv7-g1a-0.4b-20250905-ctx4096.st`, downloaded from this repository's
`models` release into `~/.Ai00` if missing. The worker starts `ai00-server`
with an explicit generated `~/.Ai00/assets/config.toml`. Tokenizer and WebUI
resources are refreshed at startup. The default port is **8080**.

The default binding is now **127.0.0.1**, not all interfaces, because the
generated config does not require authentication. Do not expose it directly
to an untrusted network. Explicit LAN binding is still available via `ip`;
add an authenticated reverse proxy/firewall before allowing remote access.

To select an existing/downloadable model, port, options and callbacks:

```4d
var $Ai00 : cs.Ai00.Ai00
var $model : 4D.File
var $event : cs.event.event
$model:=Folder(fk home folder).folder(".Ai00").file("my-model.st")
$event:=cs.event.event.new()
$event.onError:=Formula(ALERT($2.message))
$event.onTerminate:=Formula(LOG EVENT(Into 4D debug message; "Ai00 terminated"))
$Ai00:=cs.Ai00.Ai00.new(8087; $model; "https://example.com/my-model.st"; \
    {max_batch: 1; precision: "Fp32"; quant_type: "Int8"}; $event)
```

Replace the example URL with a real compatible Safetensors model URL.
`quant_type` alone does not enable quantization: the current template sets
`quant = 0`. Upstream no longer reads the legacy `embed_device` model field;
it does not choose a CPU RWKV backend. The wrapper's `onSuccess` callback
currently means the model file is available and the worker was started,
**not** that GPU/model loading or inference succeeded.

Use the port you selected (8080 for the default constructor):

```sh
curl --fail http://127.0.0.1:8080/api/oai/v1/models
curl --fail http://127.0.0.1:8080/api/oai/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello!"}],"max_tokens":64,"stream":false}'
```

The OpenAI-compatible base URL is `http://127.0.0.1:8080/api/oai/v1`,
**not** just `/v1`. See `/api-docs/` for the upstream schema. Models,
chat/completions and text completions are supported; embeddings require a
separately configured upstream `[embed]` model, not RWKV embeddings. This
does not imply support for OpenAI images, moderation, or file APIs.

```4d
var $Ai00 : cs.Ai00.Ai00
$Ai00:=cs.Ai00.Ai00.new()
$Ai00.terminate()
```

### Standalone CLI and models

The executable is **`ai00-server`**, not `ai00_rwkv_server`. Its application
arguments are `--config <FILE>`, `--ip <IP>` and `--port <PORT>` (plus
`--help`/`--version`); model/quantization settings belong in TOML.
For standalone use, run from `.build/ai00_server` so relative `assets/...`
paths resolve, edit `assets/configs/Config.toml` to point at your `.st`
model, and start:

```sh
./target/aarch64-apple-darwin/release/ai00-server \
  --config assets/configs/Config.toml --ip 127.0.0.1 --port 8080
```

Upstream's default config differs from the 4D config: it uses port 65530
and enables authentication. Set your own authentication settings; never use
its example secrets on a network. Windows standalone embedding users must
also retain `assets/ort/onnxruntime.dll`.

`.pth` models need conversion to Safetensors (`.st`). Prefer upstream's
`assets/scripts/convert_safetensors.py` with Python, `torch` and
`safetensors`, or the separately bundled legacy converter:

```sh
converter --input model.pth --output model.st
```

Use the executable's full platform-specific path above. Validate converted
models against the current engine; conversion and model compatibility are
not guaranteed by a successful CLI build.

## Suggested follow-up work

These are proposals, **not** changes included in the server build update:

| Priority | Proposal | Concrete evidence |
|---|---|---|
| High | Poll model readiness before `onSuccess`, and report failed loads | `_Model.4dm` `start()` calls `onSuccess` immediately after worker start; upstream `main.rs` queues model loading asynchronously. A model-less local smoke test served API docs but `/api/oai/v1/models` timed out. |
| High | Make downloads atomic and validate HTTP ranges/checksums | `_Model.4dm` writes directly to the final model file, trusts any existing file, and accepts both 200 and 206 for range requests without checking `Content-Range`. An interrupted download can be mistaken for a model. |
| Medium | Expose real quantization and GPU selection options | `_Config.4dm` getters hard-code `quant = 0` and `manual = 0`; `_server.4dm` consumes `quant` without applying it. `quant_type` cannot activate quantization. |
| Medium | Forward stderr/worker errors to the supplied callbacks | `_Model.4dm` stores `onStdErr`/`onStdOut`, but `_server.4dm` binds only `onTerminate`; `_CLI_Controller.4dm`'s default error/data handlers do nothing. |
| Medium | Reproducibly rebuild the converter separately | Upstream root `Cargo.toml` omits `crates/converter` from workspace members; the bundled converter binaries have no recorded revision. |
| Low | Pin the 4D component dependencies independently | `Project/Sources/dependencies.json` still requests `latest` for `event`, `workers`, and `tcp`; publishing records the resolved versions but future builds can resolve newer ones. |
| Low | Automate upstream pin proposals with release/HEAD distinction | `upstream.json` centralizes the immutable revision and asset hashes; updates should be reviewed and all native jobs should pass before publishing. |

## Documentation site

The [documentation site](https://miyako.github.io/ai00/) adopts
[local-inference-site-design v1.0.0](https://github.com/miyako/local-inference-site-design/blob/v1.0.0/SITE-DESIGN.md).
The adopted version and tagged guideline URL are recorded in `_config.yml`;
guideline upgrades are explicit, reviewed site changes, not runtime imports.
The sidebar, favicon, and local-stack illustration use an unchanged copy of
`Ai00/Resources/logo.png` at `assets/resource-logo.png`.
The original overview and `guide.html` reference anchors remain available;
`build.html` provides a focused source-build entry point.

## Attribution

This 4D integration is MIT-licensed. Ai00 is developed by the
[Ai00-X contributors](https://github.com/Ai00-X/ai00_server), based on
[web-rwkv](https://github.com/cryscan/web-rwkv). Its Cargo metadata declares
`MIT OR Apache-2.0`; its checked-in `LICENSE` is included in generated
resources. Rust dependencies, ONNX Runtime, WebUI, tokenizers and model
weights retain their respective licenses. Download models only under terms
appropriate for your use.
