import json
import logging
from abc import ABC, abstractmethod

import requests
from django.conf import settings
from liqpay.liqpay3 import LiqPay
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class NotParamsError(Exception):
    pass


class ResponsePaymentError(requests.RequestException):
    """Error getting response from liqpay"""


class Callback:
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)

    @staticmethod
    def callback(data, signature):
        sign = Callback.liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
        if sign != signature:
            logger.warning(f"Signature doesn't much, original signature {sign} ,\n"
                           f"signature from request {signature},\n data for sign - {data}\n")
            raise ValidationError({'signature': "Signature doesn't much, original signature"})
        return Callback.liqpay.decode_data_from_str(data)


class LiqPayBase(ABC):
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    request_url = "https://www.liqpay.ua/api/request"
    version = "3"
    server_url = f'{settings.DOMAIN}order/paycallback'

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def get_params(self):
        if hasattr(self, 'params'):
            self.params.update({
                'version': LiqPayBase.version,
                'server_url': self.params.get('server_url', LiqPayBase.server_url)
            })
            return self.params
        raise NotParamsError('Initialize the required attribute "params" of the dictionary type')

    def api(self):
        data = LiqPayBase.liqpay.cnb_data(self.get_params())
        signature = LiqPayBase.liqpay.cnb_signature(self.get_params())
        request_data = {"data": data, "signature": signature}
        try:
            res = requests.post(LiqPayBase.request_url, data=request_data, verify=False)
            return json.loads(res.content.decode("utf-8"))
        except requests.RequestException:
            logger.warning(
                "Error getting response from liqpay\n " f'data- {data},\n params - '
                f'{self.get_params()}\n', exc_info=True
            )


class LiqPayCard(LiqPayBase):
    def __init__(self,
                 order_id: str,
                 amount: str,
                 phone: str,
                 card: str,
                 card_exp_month: str,
                 card_exp_year: str,
                 card_cvv: str,
                 description=None,
                 save_card: bool = False):
        self.params = dict(
            action='pay',
            phone=phone,
            order_id=order_id,
            amount=amount,
            card=card,
            card_exp_month=card_exp_month,
            card_exp_year=card_exp_year,
            card_cvv=card_cvv,
            currency="UAH",
            description=description or " "
        )
        if save_card:
            self.params.update(dict(recurringbytoken=1))


class LiqPayToken(LiqPayBase):
    def __init__(self,
                 order_id: str,
                 amount: str,
                 phone: str,
                 card_token: str,
                 description=None):
        self.params = dict(
            action='paytoken',
            phone=phone,
            order_id=order_id,
            amount=amount,
            card_token=card_token,
            currency="UAH",
            description=description or " "
        )


class ReceiptLiqPay(LiqPayBase):
    def __init__(self,
                 order_id: str,
                 email: str):
        self.params = dict(
            action='ticket',
            order_id=order_id,
            email=email,
            currency="UAH"
        )
