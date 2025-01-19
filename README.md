# docchatai

### I am DocChatAI. Ask me anything about any document.

See: https://python.langchain.com/docs/how_to/

Required properties:

```dotenv
APP_DIR=[Required]
# long random string, will be used for securely signing the session cookie
APP_SECRET_KEY=[Required]
CHAT_MODEL="[Optional, default=llama3.1]"
CHAT_MODEL_PROVIDER="[Optional, default=ollama]"
CHAT_FILE=[Required]
MAX_RESULTS_PER_QUERY="[Optional, default=3]"
```