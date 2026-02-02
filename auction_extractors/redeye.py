from fastapi import Depends

from app.dependencies import Translate, TranslateLanguage
from models.auctionextractor_shopify import ShopifySearchExtractor



class RedEye(ShopifySearchExtractor):
    dependencies = [Depends(Translate)]
    transformers = [Translate.translate_from(language=TranslateLanguage.JAPANESE)]
    print(f"{transformers=}")

    @property
    def domain(self) -> str:
        return "redeye.com.au"

    @property
    def site_desc(self) -> str:
        return "Red Eye Records"
