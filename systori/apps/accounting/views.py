from django.views.generic.edit import CreateView
from .models import *
from .forms import *
from .skr03 import *

class PaymentCreate(CreateView):
    model = Payment
    form_class = PaymentForm

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        is_discount = form.cleaned_data['is_discounted']
        group = TransactionGroup.objects.create()
        partial_credit(group, self.request.project, amount, is_discount)
        form.instance.project = self.request.project
        form.instance.transaction_group = group
        return super(PaymentCreate, self).form_valid(form)

    def get_success_url(self):
        return self.object.project.get_absolute_url()