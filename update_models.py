import requests
import json

MANUAL = [
    {
        "n": "Kimi K2 (free)",
        "p": "Moonshot AI",
        "c": "chat",
        "pop": 88,
        "ctx": "128K",
        "tags": ["ru", "free", "online"],
        "d": "Открытая MoE-модель Moonshot AI: 1 трлн параметров, 32B активных. Сильна в программировании, агентных задачах и работе с инструментами, хорошо держит длинный контекст.",
        "f": "Бесплатно через OpenRouter (moonshotai/kimi-k2:free) — без привязки карты, с дневными лимитами",
        "u": "https://openrouter.ai/models/moonshotai/kimi-k2:free",
        "doc": "https://openrouter.ai/docs"
    }
]

PROVIDER_MAP = {
    'openai': 'OpenAI', 'anthropic': 'Anthropic', 'google': 'Google',
    'meta-llama': 'Meta', 'mistralai': 'Mistral', 'deepseek': 'DeepSeek',
    'qwen': 'Alibaba', 'cohere': 'Cohere', 'microsoft': 'Microsoft',
    'huggingface': 'Hugging Face', 'nvidia': 'NVIDIA', 'perplexity': 'Perplexity',
    'openrouter': 'OpenRouter', 'moonshotai': 'Moonshot AI'
}

# Точные метки для провайдеров, про которых известно наверняка.
# Всё остальное получает DEFAULT_TAGS.
PROVIDER_TAGS = {
    'Alibaba': ["ru", "free", "online"],
    'Moonshot AI': ["ru", "free", "online"],
    'DeepSeek': ["ru", "free", "online"],
    'Mistral': ["ru", "free", "online"]
}
DEFAULT_TAGS = ["ru", "limited", "online"]

def is_free(m):
    pricing = m.get('pricing', {})
    zero = str(pricing.get('prompt', '1')) == '0' and str(pricing.get('completion', '1')) == '0'
    free_tag = m.get('id', '').endswith(':free')
    return zero or free_tag

def main():
    print("Запрос актуальных данных из OpenRouter API...")
    response = requests.get('https://openrouter.ai/api/v1/models')
    if response.status_code != 200:
        print(f"Ошибка запроса к API. Код: {response.status_code}")
        return

    all_models = response.json().get('data', [])
    free_models = []

    for m in all_models:
        if not is_free(m):
            continue
        model_id = m.get('id', '')
        org_slug = model_id.split('/')[0] if '/' in model_id else 'openrouter'
        provider = PROVIDER_MAP.get(org_slug, org_slug.replace('-', ' ').title())
        tags = PROVIDER_TAGS.get(provider, DEFAULT_TAGS)
        desc = m.get('description', 'Бесплатная модель, доступная через агрегатор OpenRouter.')
        if len(desc) > 180:
            desc = desc[:177] + '...'
        free_models.append({
            "n": m.get('name', 'Unknown Model'),
            "p": provider,
            "c": "chat",
            "pop": 50,
            "ctx": str(m.get('context_length', 'N/A')),
            "tags": tags,
            "d": desc,
            "f": "Бесплатно через OpenRouter (без привязки карты)",
            "u": f"https://openrouter.ai/models/{model_id}",
            "doc": "https://openrouter.ai/docs"
        })

    existing = {item['n'] for item in free_models}
    for item in MANUAL:
        if item['n'] not in existing:
            free_models.append(item)

    with open('models.json', 'w', encoding='utf-8') as f:
        json.dump(free_models, f, ensure_ascii=False, indent=2)

    print(f"Успешно сохранено {len(free_models)} бесплатных моделей в models.json")

if __name__ == "__main__":
    main()