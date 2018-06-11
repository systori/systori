from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, ValidationError
from .workflow import Account
from .constants import BANK_CODE_RANGE


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ["name"]


class BankAccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ["code", "name"]

    def __init__(self, *args, instance=None, **kwargs):
        if instance is None:  # create form
            banks = Account.objects.banks().order_by("-code")
            if banks.exists():
                next_code = int(banks.first().code) + 1
            else:
                next_code = BANK_CODE_RANGE[0]

            if next_code <= BANK_CODE_RANGE[1]:
                # set initial only if we were able to compute code within range
                kwargs["initial"] = {"code": str(next_code)}

            kwargs["instance"] = Account(
                account_type=Account.ASSET, asset_type=Account.BANK
            )
        else:
            kwargs["instance"] = instance

        super(BankAccountForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data["code"]

        if (
            not code.isdigit()
            or int(code) < BANK_CODE_RANGE[0]
            or int(code) > BANK_CODE_RANGE[1]
        ):
            raise ValidationError(
                _(
                    "Account code must be a number between %(min)s and %(max)s inclusive."
                ),
                code="invalid",
                params={"min": BANK_CODE_RANGE[0], "max": BANK_CODE_RANGE[1]},
            )

        return code
