class ChatModels:
    @staticmethod
    def model(name: str, provider: str):
        from langchain.chat_models import init_chat_model
        return init_chat_model(name, model_provider=provider, temperature=0)

    @staticmethod
    def embeddings(name: str, provider: str):
        if provider == 'ollama':
            from langchain_ollama.embeddings import OllamaEmbeddings
            return OllamaEmbeddings(model=name)
        # TODO - Add embeddings for more providers.
        else:
            raise ValueError(f'Unsupported model provider for embeddings: {provider}')