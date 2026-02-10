class CommonFormMixin:
    form_title = ""
    template_name = "common/common_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = self.form_title
        return context
