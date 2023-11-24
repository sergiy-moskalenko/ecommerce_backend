import pytest
from factory import Factory
from faker import Faker as BaseFaker
from rest_framework import serializers

from order.validation import CardValidator

fake = BaseFaker()


class CardValidatorFactory(Factory):
    class Meta:
        model = CardValidator


@pytest.fixture
def card_validator():
    return CardValidatorFactory()


@pytest.mark.parametrize("card_type", ['mastercard', 'visa16'])
def test_valid_card_number(card_validator, card_type):
    valid_card_number = fake.credit_card_number(card_type=card_type)
    assert card_validator.is_valid(valid_card_number)


@pytest.mark.parametrize("card_type", ['mastercard', 'visa16'])
def test_invalid_card_number(card_validator, card_type):
    invalid_card_number = fake.credit_card_number(card_type=card_type)[::-1] + '1'  # Generate an invalid card number
    with pytest.raises(serializers.ValidationError):
        card_validator(invalid_card_number)


def test_invalid_input_type(card_validator):
    with pytest.raises(serializers.ValidationError):
        card_validator('not_a_valid_card_number')
