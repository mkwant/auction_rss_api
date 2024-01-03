import uuid

import httpx


async def translate_text(client: httpx.AsyncClient,
                         text: str,
                         from_language: str,
                         to_language: str,
                         ms_translate_api_key: str,
                         ms_translate_api_location: str,
                         api_version: float = '3.0'
) -> str:
    base_url = 'https://api.cognitive.microsofttranslator.com'
    endpoint = 'translate'

    url = f'{base_url}/{endpoint}?api-version={api_version}&from={from_language}&to={to_language}'

    headers = {
        'Ocp-Apim-Subscription-Key': ms_translate_api_key,
        'Ocp-Apim-Subscription-Region': ms_translate_api_location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    payload = [{'text': text}]

    r = await client.post(url, headers=headers, json=payload)
    try:
        result = r.json()[0]['translations'][0]['text']
    except Exception:
        print(r.json())
        raise ConnectionError(f'{r.json}')
    return result
