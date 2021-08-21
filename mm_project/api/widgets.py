from django.forms import DateInput


class FengyuanChenDatePickerInput(DateInput):
    """
    https://github.com/fengyuanchen/datepicker
    """
    template_name = 'widgets/datepicker.html'
