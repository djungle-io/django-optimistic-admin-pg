from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.test import TestCase

from optimisticadmin.expressions import XMin
from optimisticadmin.mixins import OptimisticAdminMixin, OptimisticAdminModelFormMixin


class OptimisticAdminMixinTestCase(TestCase):
    def test_get_queryset_annotated_with_row_version(self):
        class BaseClass:
            def get_queryset(self, request):
                return ContentType.objects.all()[:10]

        class TestClass(OptimisticAdminMixin, BaseClass):
            pass

        qs = TestClass().get_queryset(None)
        self.assertTrue(all(hasattr(q, "row_version") for q in qs))


class TestForm(OptimisticAdminModelFormMixin, forms.ModelForm):
    row_version = forms.IntegerField(required=False)

    class Meta:
        fields = ("app_label", "model", "row_version")
        model = ContentType


class OptimisticAdminModelFormMixinTestCase(TestCase):
    def test_does_nothing_on_new_object(self):
        form = TestForm({"app_label": "app_label", "model": "model"})
        instance = form.save()
        self.assertTrue(instance)

    def test_does_nothing_without_row_version(self):
        instance = ContentType.objects.first()
        data = model_to_dict(instance)
        form = TestForm(data, instance=instance)
        form.save()

    def test_is_valid_with_same_row_version(self):
        instance = ContentType.objects.annotate(row_version=XMin()).first()
        data = model_to_dict(instance)
        data["row_version"] = instance.row_version
        form = TestForm(data, instance=instance)
        self.assertTrue(form.is_valid())

    def test_is_not_valid_with_different_row_version(self):
        instance = ContentType.objects.annotate(row_version=XMin()).first()
        data = model_to_dict(instance)
        data["row_version"] = -1
        form = TestForm(data, instance=instance)
        self.assertFalse(form.is_valid())
        expected_error_msg = [
            "You are trying to update a model that has changed in the meantime, better reload "
            "the page and start again to avoid overriding data unexpectedly."
        ]
        self.assertEqual(form.errors["__all__"], expected_error_msg)
