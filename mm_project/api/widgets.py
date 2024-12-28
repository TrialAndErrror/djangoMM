from django.forms import DateInput
from django.forms.widgets import TextInput


class FengyuanChenDatePickerInput(DateInput):
    """
    https://github.com/fengyuanchen/datepicker
    """
    template_name = 'widgets/datepicker.html'


class BalanceWidget(TextInput):
    template_name = 'widgets/balance-changing-widget.html'

    def __init__(self, endpoint_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint_url = endpoint_url

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['endpoint_url'] = self.endpoint_url
        return context

