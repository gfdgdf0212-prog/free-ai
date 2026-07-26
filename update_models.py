import requests
import json

def main():
    print("Запрос актуальных данных из OpenRouter API...")
    response = requests.get('https://openrouter.ai/api/v1/models')
    
    if response.status_code != 200:
        print(f"Ошибка запроса к API. Код: {response.status_code}")
        return
    
    all_models = response.json().get('data', [])
    free_models = []
    
    # Словарь для перевода технических slug-ов в красивые названия провайдеров
    PROVIDER_MAP = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic',
        'google': 'Google',
        'meta-llama': 'Meta',
        'mistralai': 'Mistral',
        'deepseek': 'DeepSeek',
        'qwen': 'Alibaba',
        'cohere': 'Cohere',
        'microsoft': 'Microsoft',
        'huggingface': 'Hugging Face',
        'nvidia': 'NVIDIA',
        'perplexity': 'Perplexity',
        'openrouter': 'OpenRouter'
    }
    
    for m in all_models:
        pricing = m.get('pricing', {})
        # Проверяем, что модель полностью бесплатная
        if str(pricing.get('prompt', '1')) == '0' and str(pricing.get('completion', '1')) == '0':
            
            model_id = m.get('id', '')
            
            # Извлекаем организацию из ID (всё, что до первого слеша)
            org_slug = model_id.split('/')[0] if '/' in model_id else 'openrouter'
            
            # Получаем красивое название. Если его нет в словаре, просто делаем первую букву заглавной
            provider = PROVIDER_MAP.get(org_slug, org_slug.replace('-', ' ').title())
            
            # Формируем описание
            desc = m.get('description', 'Бесплатная модель, доступная через агрегатор OpenRouter.')
            if len(desc) > 180:
                desc = desc[:177] + '...'
            
            free_models.append({
                "n": m.get('name', 'Unknown Model'),
                "p": provider, # <-- Здесь теперь точный провайдер из API!
                "c": "chat",
                "pop": 50,
                "ctx": str(m.get('context_length', 'N/A')),
                "tags": ["ru", "limited", "online"],
                "d": desc,
                "f": "Бесплатно через OpenRouter (без привязки карты)",
                "u": f"https://openrouter.ai/models/{model_id}",
                "doc": "https://openrouter.ai/docs"
            })
    
    # Сохраняем в файл
    with open('models.json', 'w', encoding='utf-8') as f:
        json.dump(free_models, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Успешно сохранено {len(free_models)} бесплатных моделей в models.json")

if __name__ == "__main__":
    main()
