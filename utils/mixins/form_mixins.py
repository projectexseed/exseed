from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper


class CrispyFormMixin(object):
    @property
    def helper(self):
        if not hasattr(self, '_helper'):
            self._helper = FormHelper()
            submit_value = "Submit"
            if hasattr(self, 'submit_value'):
                submit_value = self.submit_value
            self._helper.add_input(Submit('submit', submit_value, css_class="pull-right"))
            self._helper.form_class = 'form-horizontal col-md-11'
            self._helper.label_class = 'col-md-3'
            self._helper.field_class = 'col-md-9'
        return self._helper
