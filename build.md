---
layout: default
title: Build Ai00 from source
nav_title: Build
content_class: guide
---

<p class="eyebrow">Native server / reproducible source</p>

# Build Ai00 from source

Build the pinned upstream server for your own machine, then stage its Resources
overlay for the 4D component. This is a native build, not a cross-compilation
recipe. For released components, start with [installation]({{ '/guide.html#install-the-4d-component' | relative_url }}).

## Prepare your machine

Install Git with Git LFS, Python 3.9+, Rust/rustup, and native build tools:
Xcode Command Line Tools on macOS, or Visual Studio C++ Build Tools and the
Windows SDK on Windows. Network access is required for source, LFS assets,
crates, and the default ONNX Runtime build dependency.

| Host | Rust target |
|---|---|
| Apple Silicon macOS | `aarch64-apple-darwin` |
| Intel macOS | `x86_64-apple-darwin` |
| Windows x64 | `x86_64-pc-windows-msvc` |

RWKV inference needs a WebGPU-compatible GPU/backend and enough model memory.
The 4D launcher does not support Linux or Windows ARM.

## Build the pinned server

Run these commands for Apple Silicon; substitute your target from the table
on Intel Mac or Windows, and use `python` instead of `python3` on Windows.

```sh
git clone https://github.com/miyako/ai00.git
cd ai00
git lfs install
rustup toolchain install 1.91.0 --profile minimal
rustup target add --toolchain 1.91.0 aarch64-apple-darwin
python3 scripts/build-server.py --target aarch64-apple-darwin
```

The script builds upstream commit `54ddbd6818499b11bfd0469d2ea59577d8076c92`
(release v0.7.1) with the locked dependencies and default features, then checks
`--help` and `--version`. The upstream Cargo package reports **0.6.2**;
that is not the release-tag version. See the [version and provenance reference]({{ '/guide.html#upstream-version' | relative_url }}).

## Stage and run

The output in `dist/<target>/` is a Resources overlay, not a standalone
component. It contains the server, tokenizer, WebUI, licenses, provenance,
checksums, and the Windows ONNX Runtime DLL where applicable.

For local 4D development on Apple Silicon:

```sh
cp -R dist/aarch64-apple-darwin/. Ai00/Resources/
```

Open the 4D project after staging the overlay, restore its declared component
dependencies, and follow [Use from 4D]({{ '/guide.html#use-from-4d' | relative_url }}).
For standalone use, edit `.build/ai00_server/assets/configs/Config.toml` to
select a compatible `.st` model, then run from the upstream checkout:

```sh
cd .build/ai00_server
./target/aarch64-apple-darwin/release/ai00-server \
  --config assets/configs/Config.toml --ip 127.0.0.1 --port 8080
```

The upstream config enables authentication and defaults to port 65530; the
command above explicitly overrides the listener. Set your own authentication
settings rather than using upstream example secrets. Windows embedding users
must retain `assets/ort/onnxruntime.dll`. Follow the
[CLI and model reference]({{ '/guide.html#standalone-cli-and-models' | relative_url }})
for model conversion and compatibility limits, and the
[first-request example]({{ '/#quickstart' | relative_url }}) once your model is ready.

## Component publishing

Publishing requires successful native builds for all three targets, verified
overlays, the existing tool4d component build, and Apple signing/notarization.
The legacy converters are not rebuilt by the server workflow and have no
recorded source revision. See the complete
[build reference]({{ '/guide.html#build-the-server-from-source' | relative_url }})
and [release pipeline]({{ '/guide.html#ci-and-component-publishing' | relative_url }})
before preparing a component release.
