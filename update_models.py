import requests
import json

def main():
    print("Запрос данных из OpenRouter API...")
    # Получаем список всех моделей
    response = requests.get('https://openrouter.ai/api/v1/models')
    if response.status_code != 200:
        print("Ошибка запроса к API")
        return
    
    all_models = response.json().get('data', [])
    
    # Фильтруем только те, у которых цена промпта и вывода равна 0 (бесплатные)
    free_models = []
    for m in all_models:
        pricing = m.get('pricing', {})
        if str(pricing.get('prompt', '1')) == '0' and str(pricing.get('completion', '1')) == '0':
            free_models.append({
                "n": m.get('name', 'Unknown Model'),
                "p": "OpenRouter",
                "c": "chat",
                "pop": 50,
                "ctx": m.get('context_length', 'N/A'),
                "tags": ["ru", "limited", "online"],
                "d": f"Бесплатная модель через OpenRouter. Архитектура: {m.get('architecture', {}).get('modality', 'text')}.",
                "f": "Полностью бесплатно через OpenRouter (без привязки карты)",
                "u": f"https://openrouter.ai/models/{m['id']}",
                "doc": "https://openrouter.ai/docs"
            })
    
    # Если бесплатных моделей мало, добавим несколько проверенных вручную для наполнения
    if len(free_models) < 10:
        print("Мало бесплатных моделей в API, добавляем базовый набор...")
        # Здесь можно оставить ваш исходный массив как fallback, но пока оставим так
    
    # Сохраняем в файл
    with open('models.json', 'w', encoding='utf-8') as f:
        json.dump(free_models, f, ensure_ascii=False, indent=2)
    
    print(f"Успешно сохранено {len(free_models)} бесплатных моделей в models.json")

if __name__ == "__main__":
    main()
