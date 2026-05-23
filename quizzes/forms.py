from django import forms
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from .models import AnswerVariant, Question, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "description", "image"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название квиза",
                    "maxlength": 200,
                    "minlength": 3,
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Описание (необязательно)",
                    "maxlength": 1000,
                    "rows": 4,
                },
            ),
        }


class AnswerVariantForm(forms.ModelForm):
    class Meta:
        model = AnswerVariant
        fields = ["text", "is_correct", "order"]
        widgets = {
            "text": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Вариант ответа"}
            ),
            "is_correct": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.HiddenInput(),
        }


class BaseAnswerVariantFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.question_type = kwargs.pop("question_type", "single")
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        active_forms = 0
        correct_count = 0
        texts = set()

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue

            text = form.cleaned_data.get("text", "").strip()
            is_correct = form.cleaned_data.get("is_correct", False)

            if text:
                active_forms += 1
                if text.lower() in texts:
                    raise forms.ValidationError(
                        "Варианты ответов не должны повторяться."
                    )
                texts.add(text.lower())

            if is_correct:
                correct_count += 1

        if active_forms < 2:
            raise forms.ValidationError("Должно быть минимум 2 варианта ответа.")

        if correct_count < 1:
            raise forms.ValidationError("Укажите хотя бы один правильный ответ.")
        if self.question_type == "single" and correct_count > 1:
            raise forms.ValidationError(
                "Для вопроса типа 'Один правильный ответ' может быть только один "
                "верный вариант."
            )


AnswerVariantFormSet = inlineformset_factory(
    Question,
    AnswerVariant,
    form=AnswerVariantForm,
    formset=BaseAnswerVariantFormSet,
    extra=2,
    min_num=2,
    max_num=100,
    can_delete=True,
    validate_min=False,
)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "question_type", "points", "timer"]
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "question_type": forms.Select(attrs={"class": "form-control"}),
            "points": forms.NumberInput(attrs={"class": "form-control"}),
            "timer": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Необязательно"}
            ),
        }

    def clean_points(self):
        points = self.cleaned_data.get("points")
        if points is not None and (points < 1 or points > 100):
            raise forms.ValidationError("Баллы должны быть от 1 до 100.")
        return points

    def clean_timer(self):
        timer = self.cleaned_data.get("timer")
        if timer is not None and (timer < 10 or timer > 3600):
            raise forms.ValidationError("Таймер должен быть от 10 до 3600 секунд.")
        return timer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.question_type == "multiple":
            self.fields["text"].help_text = "Отметьте все правильные ответы"
