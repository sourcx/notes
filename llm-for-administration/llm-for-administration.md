# LLM for Administration

ollama run qwen3.5:9b

ollama create qwen3.5-9b-32k -f Modelfile.9b
ollama run qwen3.5-9b-32k

ollama create qwen3-14b-16k -f Modelfile.14b

ollama run qwen3-14b-16k
ollama ps
 

cat ~/.config/systemd/user/ollama.service.d/override.conf
[Service]
Environment=OLLAMA_FLASH_ATTENTION=1
Environment=OLLAMA_KV_CACHE_TYPE=q8_0
