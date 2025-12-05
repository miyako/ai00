---
layout: default
---

![version](https://img.shields.io/badge/version-20%2B-E23089)
![platform](https://img.shields.io/static/v1?label=platform&message=mac-intel%20|%20mac-arm%20|%20win-64&color=blue)
[![license](https://img.shields.io/github/license/miyako/ai00)](LICENSE)
![downloads](https://img.shields.io/github/downloads/miyako/ai00/total)

# Use Ai00 from 4D

#### Abstract

[**Ai00**](https://github.com/Ai00-X/ai00_server) is an inference server secifically designed for the [RWKV](https://huggingface.co/blog/rwkv) language model. Unlike transformer-based models like Llama, Mistral, or GPT, RWKV (Raven's World-Knowledge Vectors) is a recurrent neural network which means it can have an infinite context on low RAM (it uses the exact same amount of RAM regardless of the number of tokens).

#### Usage

Instantiate `cs.Ai00.Ai00` in your *On Startup* database method:

```4d
var $Ai00 : cs.Ai00

If (False)
    $Ai00:=cs.Ai00.new()  //default
Else 
    var $modelsFolder : 4D.Folder
    $modelsFolder:=Folder(fk home folder).folder(".Ai00")
    var $file : 4D.File
    $file:=$modelsFolder.file("RWKV-x070-World-0.4B-v2.9-20250107-ctx4096.st")
    $URL:="https://modelscope.cn/models/shoumenchougou/RWKV-7-World-ST/resolve/master/RWKV-x070-World-0.4B-v2.9-20250107-ctx4096.st"
    var $port : Integer
    $port:=8080
    $Ai00:=cs.Ai00.new($port; $file; $URL; {\
    quant_type: "Int8"; \
    precision: "Fp16"}; Formula(ALERT(This.file.name+($1.success ? " started!" : " did not start..."))))
End if 
```

Unless the server is already running (in which case the costructor does nothing), the following procedure runs in the background:

1. The specified model is download via HTTP
2. The `ai00-server` program is started

Now you can test the server:

```
curl -X GET http://127.0.0.1:8080/api/oai/v1/models
```

```
curl -X 'POST' \
  'http://127.0.0.1:8080/api/oai/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "max_tokens": 1000,
  "messages": [
    {
      "content": "Hi!",
      "role": "user"
    },
    {
      "content": "Hello, I am your AI assistant. If you have any questions or instructions, please let me know!",
      "role": "assistant"
    },
    {
      "content": "Tell me about water.",
      "role": "user"
    }
  ],
  "names": {
    "assistant": "Assistant",
    "user": "User"
  },
  "sampler": {
    "frequency_penalty": 0.3,
    "penalty_decay": 0.99654026,
    "presence_penalty": 0.3,
    "temperature": 1,
    "top_k": 128,
    "top_p": 0.5,
    "type": "Nucleus"
  },
  "state": "00000000-0000-0000-0000-000000000000",
  "stop": [
    "\n\nUser:"
  ],
  "stream": false,
  "template": {
    "prefix": "{assistant}:",
    "record": "{role}: {content}",
    "sep": "\n\n"
  }
}'
```

The full list of endpoints are listsed at `http://127.0.0.1:8080/api-docs/`.

Finally to terminate the server:

```4d
var $Ai00 : cs.Ai00.Ai00
$Ai00:=cs.Ai00.Ai00.new()
$Ai00.terminate()
```

#### Models

Models in .pth format can be downloaded from [huggingface.co](https://huggingface.co/BlinkDL/rwkv7-g1/resolve/main/rwkv7-g1a-0.4b-20250905-ctx4096.pth) or [modelscope.cn](https://modelscope.cn/models/RWKV/rwkv7-g1/resolve/master/rwkv7-g1a-0.4b-20250905-ctx4096.pth).

Ai00 can't use a .pth model directly. You can use python to [convert](https://github.com/Ai00-X/ai00_server?tab=readme-ov-file#convert-the-model) the model from .pth to .st.

You can also use the `converter` tool in `/RESOURCES/`. 

```
converter --input model.pth --output model.st
```

#### AI Kit compatibility

The API is compatibile with [Open AI](https://platform.openai.com/docs/api-reference/embeddings). 

|Class|API|Availability|
|-|-|:-:|
|Models|`/v1/models`|✅|
|Chat|`/v1/chat/completions`|✅|
|Images|`/v1/images/generations`||
|Moderations|`/v1/moderations`||
|Embeddings|`/v1/embeddings`||
|Files|`/v1/files`||

#### Why Ai00

Ai00 is designed for RWKV models, which is different from LLaMA and has distinct strengths.

The groundbreaking paper "Attention is All You Need" (2017) by researchers at Google enabled parallel processing, a key differentiator from prior sequential models like RNNs. 

Before 2017, AI processed text sequentially from start to end. The architecture had a major flaw, that it couldn't be parallelised since you can't process Word 3 until you finished processing Word 2.

The Transformer architecture allowed the computer to look at an entire sentence at once, rather than one word at a time. This unlocked the ability to use massive GPU clusters to train on the entire internet, giving birth to GPT, BERT, and Claude.

Attention, or self-attention, allows the model to weigh the relevance of every word against every other word in a sentence, regardless of how far apart they are. 

To calculate attention, the model must compare every token to every other token. This means the memory required increases by 4x if you double the length of the prompt and 9x of you triple the length. Running very long conversations on standard Transformers (like Llama 3 or Mistral) is extremely memory-heavy.

Ai00 runs the RWKV model, which uses a "Linear Attention" approach. It trains like a Transformer (fast/parallel) but runs like an RNN (sequential). The amount of RAM is fixed regardless of whether the conversation is 10 words long or 100,000 words long. 

##### LLaMA (Transformer)
- Uses self-attention
- Needs to store a KV cache for every token
- Memory grows with context

##### RWKV (Recurrent Transformer Hybrid)

- No attention at inference
- Keeps only a small hidden state
- Memory does not grow with context
- Good for text-generation with long memory
- Not a good embedding model
