import re

from rest_framework import serializers


class CardValidator:
    __message = 'Card number is invalid.'
    visa_cc = re.compile(r'^4[0-9]{3}$')
    mastercard_cc = re.compile(r'^(5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[0-1][0-9]|2720)$')

    __cc_patterns = {"Visa": visa_cc,
                     "Mastercard": mastercard_cc}

    def __init__(self):
        self._cc_patterns = CardValidator.__cc_patterns
        self.message = CardValidator.__message

    def __call__(self, value):
        if not self.is_valid(value):
            raise serializers.ValidationError(self.message)

    def _digit_check(self, cc_number):
        if not cc_number.isdecimal():
            raise serializers.ValidationError(self.message)
        return cc_number

    def _luhn_check(self, cc_number):
        digits = list(map(int, self._digit_check(cc_number)))
        odd_sum = sum(digits[-1::-2])
        even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
        return (odd_sum + even_sum) % 10 == 0

    def _iin_check(self, cc_number):
        for _, regexp in self._cc_patterns.items():
            if regexp.match(self._digit_check(cc_number)[:4]):
                return True

    def is_valid(self, cc_number):
        return self._luhn_check(cc_number) and self._iin_check(cc_number)
