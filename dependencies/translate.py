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
    result = r.json()[0]['translations'][0]['text']
    return result

#
# def main():
#     text_jpn = ['戦場のメリークリスマス 4K修復版 大規模ロードショー パンフレット Ryuichi Sakamoto 坂本龍一 DAVID BOWIE デヴィッドボウイ 大島渚 12',
#                 '[MT][S060060] 未使用 デビッド・ボウイ 東芝EMI特製紙ジャケ収納ボックス※DU特典ではありません',
#                 'IGGY POP イギーポップ The Idiot 帯付 国内盤◎中古/再生未確認/ノークレームで/盤面スレ汚れ/PUNK/プロデュース DAVID BOWIE',
#                 '戦場のメリークリスマス 4K修復版 B2(約73×51㎝)アート ポスターB デヴィッド・ボウイ DAVID BOWIE 大島渚 坂本龍一 チラシ付 未使用',
#                 'デビッドボウイ EP チェンジス',
#                 'ビギナーズ / David Bowie ep '
#                 ]
#
#     client = httpx.AsyncClient()
#
#     for i in text_jpn:
#
#         result = await translate_text(client=client, text=i, from_language='ja', to_language='en')
#
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
