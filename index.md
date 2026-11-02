---
layout: default
title: Local RWKV inference, connected to 4D
nav_title: Overview
---

<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow"><span class="status-dot" aria-hidden="true"></span> Local inference / 4D integration</p>
    <h1>Local RWKV.<br><span>Connected to 4D.</span></h1>
    <p class="lede">Bring RWKV language models into your application. Run locally on Mac or Windows, with a 4D component that handles the server lifecycle.</p>
    <div class="actions">
      <a class="button primary" href="#quickstart">Make your first request <span aria-hidden="true">&rarr;</span></a>
      <a class="button" href="{{ '/guide.html#install-the-4d-component' | relative_url }}">Get the component</a>
    </div>
  </div>
  <div class="stack-panel" role="group" aria-label="Local inference stack: 4D connects to Ai00 over loopback HTTP; Ai00 loads RWKV Safetensors weights">
    <div class="stack-header"><span class="eyebrow">The local stack</span><span class="stack-tag">On your machine</span></div>
    <div class="stack-row"><span class="app-mark" aria-hidden="true">4D</span><div><strong>Your application</strong><span>4D 20+ component</span></div></div>
    <div class="stack-connector">HTTP · 127.0.0.1:8080<br>/api/oai/v1</div>
    <div class="stack-engine">
      <img src="{{ site.logo | relative_url }}" alt="" width="52" height="52">
      <div><strong>Ai00</strong><span>RWKV inference / WebGPU</span></div>
    </div>
    <div class="stack-connector">loads</div>
    <div class="stack-row"><span class="model-mark" aria-hidden="true">.st</span><div><strong>RWKV model weights</strong><span>Safetensors · downloaded separately</span></div></div>
    <div class="stack-footer"><span>Models · Chat · Text completions</span><span>GPU backend required; no CUDA or Python for inference.</span></div>
  </div>
  <div class="platform-strip"><span>Apple Silicon</span><span>Intel Mac</span><span>Windows x64</span><span>4D 20+</span></div>
</section>

<section aria-labelledby="paths-title">
  <p class="eyebrow">Two ways in</p>
  <h2 id="paths-title">Your model. Your workflow.</h2>
  <div class="cards">
    <a class="card" href="{{ '/guide.html#use-from-4d' | relative_url }}">
      <span class="card-number">01 / 4D component</span>
      <h3>Make it part of your app <span aria-hidden="true">&nearr;</span></h3>
      <p>Start the server, resolve a model, and manage its process from 4D. Talk to it over a local HTTP API.</p>
      <span class="card-link">Integrate with 4D &rarr;</span>
    </a>
    <a class="card" href="{{ '/build.html' | relative_url }}">
      <span class="card-number">02 / Native server</span>
      <h3>Take the direct route <span aria-hidden="true">&nearr;</span></h3>
      <p>Build the pinned upstream source for your machine, configure a compatible model, and use your own HTTP client.</p>
      <span class="card-link">Build &amp; run &rarr;</span>
    </a>
  </div>
</section>

<section id="requirements" aria-labelledby="requirements-title" markdown="1">
<p class="eyebrow">Before you begin</p>
<h2 id="requirements-title">Local doesn't mean one platform.</h2>

Ai00 supports Apple Silicon, Intel macOS, and Windows x64. Inference needs a **WebGPU-compatible GPU/backend** and enough memory for your model. It is not a CPU-only RWKV server.

| You need | What to know |
|---|---|
| A supported host | macOS 11+ (also subject to your 4D version), or Windows x64 with current graphics drivers and the Visual C++ x64 runtime. |
| A compatible GPU | Metal on macOS; Vulkan/DX12 where available on Windows. No CUDA or Python required for inference. |
| A compatible model | Safetensors (`.st`) RWKV weights. The default 4D model downloads separately on first launch. Check its license and memory requirements. |
| 4D 20+ | For component integration. Make `event`, `workers`, and `tcp` dependencies available to the host project. |

<div class="callout" markdown="1">
**Recurrent by design.**
RWKV keeps a fixed-size recurrent inference state instead of a growing transformer KV cache. That is not a promise of unlimited effective model context.
</div>
</section>

<section id="quickstart" aria-labelledby="quickstart-title" markdown="1">
<p class="eyebrow">A short path to inference</p>
<h2 id="quickstart-title">From 4D to a first conversation.</h2>

[Install the released component and its dependencies]({{ '/guide.html#install-the-4d-component' | relative_url }}), then create the shared instance in **On Startup**. The first launch downloads the default model into `~/.Ai00` if it is missing.

<div class="code-heading"><span>01 / Start the component</span><span>4D</span></div>

```4d
var $Ai00 : cs.Ai00.Ai00
$Ai00:=cs.Ai00.Ai00.new()
```

The default listener is `127.0.0.1:8080`. Model downloads and GPU loading take time: the wrapper's `onSuccess` callback signals worker startup, **not inference readiness**. Retry model discovery until it succeeds before sending a request.

<div class="code-heading"><span>02 / Discover the model</span><span>Shell</span></div>

```sh
curl --fail http://127.0.0.1:8080/api/oai/v1/models
```

<div class="code-heading"><span>03 / Send a message</span><span>Shell</span></div>

```sh
curl --fail http://127.0.0.1:8080/api/oai/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [{"role": "user", "content": "Hello from 4D!"}],
    "max_tokens": 64,
    "stream": false
  }'
```

<div class="callout" markdown="1">
**Keep it local.** The generated 4D configuration does not require authentication. Keep the loopback binding unless you deliberately secure remote access with authentication and network controls.
</div>
</section>

<section class="api-section" aria-labelledby="api-title" markdown="1">
<p class="eyebrow">A familiar interface, with clear boundaries</p>
<h2 id="api-title">HTTP, without the round trip to a hosted service.</h2>

Use the OpenAI-compatible base URL **`/api/oai/v1`**, not just `/v1`. Model discovery, chat completions, and text completions are supported. Embeddings require a separate upstream embedding model; they are not RWKV embeddings. Don't assume images, moderation, or file APIs.

[Explore configuration, models, and the full integration guide &rarr;]({{ '/guide.html' | relative_url }})
</section>
