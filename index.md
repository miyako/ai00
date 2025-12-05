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
curl -X POST http://127.0.0.1:8080/api/oai/v1/embeds \
     -H "Content-Type: application/json" \
     -d '{"input":"The Eiffel Tower is located in the city of","max_tokens":510,"prefix":"query:"}'
```

Or, use AI Kit:

```4d
var $AIClient : cs.AIKit.OpenAI
$AIClient:=cs.AIKit.OpenAI.new()
$AIClient.baseURL:="http://127.0.0.1:8080/api/oai/v1"

var $text : Text
$text:="The quick brown fox jumps over the lazy dog."

var $responseEmbeddings : cs.AIKit.OpenAIEmbeddingsResult
$responseEmbeddings:=$AIClient.embeddings.create($text)
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
