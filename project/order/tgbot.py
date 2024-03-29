import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_tg_url(method: str) -> str:
    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/{method}"
    return url


def send_message_to_tg(text: str) -> None:
    params = {'chat_id': settings.TG_CHAT_ID, 'text': text}
    url = get_tg_url(method='sendMessage')

    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
    except requests.RequestException:
        logger.error("Error", exc_info=True)
