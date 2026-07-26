import requests
import json

# БЕЛЫЙ СПИСОК провайдеров, чьи open-source модели роботу разрешено ДОБАВЛЯТЬ поверх ваших.
# Сейчас пуст — значит робот ничего не добавляет и ничего не стирает: ваш каталог в полной безопасности.
# Захотите авто-подтяжку open-source — впишите сюда имена провайдеров, например: ['DeepSeek','Alibaba','Mistral']
AUTO_PROVIDERS = []

PROVIDER_MAP = {
    'openai': 'OpenAI', 'anthropic': 'Anthropic', 'google': 'Google',
    'meta-llama': 'Meta', 'mistralai': 'Mistral', 'deepseek': 'DeepSeek',
    'qwen': 'Alibaba', 'cohere': 'Cohere', 'microsoft': 'Microsoft',
    'huggingface': 'Hugging Face', 'nvidia': 'NVIDIA', 'perplexity': 'Perplexity',
    'openrouter': 'OpenRouter', 'moonshotai': 'Moonshot AI'
}
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
    # 1) читаем текущий каталог — это ВАША ручная часть, она неприкасаема
    try:
        with open('models.json', 'r', encoding='utf-8') as f:
            current = json.load(f)
    except Exception:
        current = []
    manual = [x for x in current if x.get('src') != 'auto']

    # 2) авто-часть строим ТОЛЬКО если белый список не пуст (иначе робот спит)
    auto = []
    if AUTO_PROVIDERS:
        print("Запрос OpenRouter для белого списка провайдеров...")
        r = requests.get('https://openrouter.ai/api/v1/models')
        if r.status_code == 200:
            for m in r.json().get('data', []):
                if not is_free(m):
                    continue
                mid = m.get('id', '')
                slug = mid.split('/')[0] if '/' in mid else 'openrouter'
                prov = PROVIDER_MAP.get(slug, slug.replace('-', ' ').title())
                if prov not in AUTO_PROVIDERS:
                    continue
                tags = PROVIDER_TAGS.get(prov, DEFAULT_TAGS)
                desc = m.get('description', 'Бесплатная модель через агрегатор OpenRouter.')
                if len(desc) > 180:
                    desc = desc[:177] + '...'
                auto.append({
                    "n": m.get('name', 'Unknown Model'),
                    "p": prov,
                    "c": "chat",
                    "pop": 50,
                    "ctx": str(m.get('context_length', 'N/A')),
                    "tags": tags,
                    "d": desc,
                    "f": "Бесплатно через OpenRouter (без привязки карты)",
                    "u": f"https://openrouter.ai/models/{mid}",
                    "doc": "https://openrouter.ai/docs",
                    "src": "auto"
                })

    # 3) склеиваем: ваши модели + свежие auto. Дубли по имени убираем в пользу ваших.
    manual_names = {x['n'] for x in manual}
    auto = [x for x in auto if x['n'] not in manual_names]
    result = manual + auto

    with open('models.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"manual={len(manual)} auto={len(auto)} total={len(result)}")

if __name__ == "__main__":
    main()