from django.core.exceptions import ValidationError

from .expressions import XMin


class OptimisticAdminModelFormMixin:
    """Mixin for an admin ModelForm

    This mixin checks that the row version when form data has been read is still the same.
    The form must include a `row_version` field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        row_version = getattr(self.instance, "row_version", None)
        if row_version:
            self.fields["row_version"].initial = row_version

    def _adding_instance(self):
        return self.instance._state.adding

    def clean(self):
        super().clean()

        if not self._adding_instance():
            previous_row_version = self.cleaned_data.get("row_version")

            if previous_row_version:
                model_class = self.instance.__class__
                new_instance_qs = model_class.objects.filter(id=self.instance.id).annotate(
                    row_version=XMin()
                )
                current_row_version = new_instance_qs.values_list("row_version", flat=True).first()

                if previous_row_version != current_row_version:
                    raise ValidationError(
                        "You are trying to update a model that has changed in the meantime,"
                        " better reload the page and start again to avoid overriding data unexpectedly."
                    )


class OptimisticAdminMixin:
    """Mixin for a ModelAdmin

    This mixin annotate the admin queryset with the row xmin value from PostgreSQL.
    """

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(row_version=XMin())
        return queryset
