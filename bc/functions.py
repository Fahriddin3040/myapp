from typing import Union

from bc.models import Operations


def history(user_id):
	values = Operations.objects.filter(user_id=user_id)
	balance = 0
	for item in values:
		if item.typ == 1:
			balance -= item.amount
		else:
			balance += item.amount
	return balance


def get_balance(user) -> Union[float, int]:
	balance = user.balance + history(user.id)
	return balance
