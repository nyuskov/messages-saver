from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import ProfileForm
from .models import Profile


class IndexView(FormView):
    template_name = "mails/index.html"
    form_class = ProfileForm
    success_url = reverse_lazy("mails:index")

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(
            **self.get_form_kwargs(),
            instance=Profile.objects.first())

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
