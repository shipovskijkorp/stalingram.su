from pathlib import Path

from django import forms


MAX_ATTACHMENTS = 10
MAX_FILE_SIZE = 25 * 1024 * 1024
MAX_TOTAL_SIZE = 100 * 1024 * 1024
MEDIA_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp",
    ".mp4", ".webm", ".mov", ".m4v",
}


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        result = single_file_clean(data, initial)
        return [result] if result else []


class MessageForm(forms.Form):
    MODE_MEDIA = "media"
    MODE_FILE = "file"

    text = forms.CharField(required=False, max_length=4096)
    reply_to = forms.IntegerField(required=False, min_value=1)
    attachment_mode = forms.ChoiceField(
        required=False,
        choices=((MODE_MEDIA, "Медиа"), (MODE_FILE, "Файл")),
        initial=MODE_MEDIA,
    )
    attachments = MultipleFileField(required=False)

    def clean_text(self):
        return self.cleaned_data.get("text", "").strip()

    def clean_attachment_mode(self):
        return self.cleaned_data.get("attachment_mode") or self.MODE_MEDIA

    def clean_attachments(self):
        files = self.cleaned_data.get("attachments") or []
        if len(files) > MAX_ATTACHMENTS:
            raise forms.ValidationError(
                f"За раз можно отправить не больше {MAX_ATTACHMENTS} файлов."
            )

        mode = self.cleaned_data.get("attachment_mode") or self.MODE_MEDIA
        total_size = 0
        for uploaded in files:
            extension = Path(uploaded.name).suffix.lower()
            content_type = (getattr(uploaded, "content_type", "") or "").lower()
            if extension == ".gif" or content_type == "image/gif":
                raise forms.ValidationError("GIF в Stalingram пока отключены.")
            if mode == self.MODE_MEDIA:
                if extension not in MEDIA_EXTENSIONS or not (
                    content_type.startswith("image/") or content_type.startswith("video/")
                ):
                    raise forms.ValidationError(
                        "В режиме медиа можно отправлять только изображения и видео."
                    )
            if uploaded.size > MAX_FILE_SIZE:
                raise forms.ValidationError("Один файл должен быть не больше 25 МБ.")
            total_size += uploaded.size

        if total_size > MAX_TOTAL_SIZE:
            raise forms.ValidationError(
                "Общий размер вложений должен быть не больше 100 МБ."
            )
        return files

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("text") and not cleaned.get("attachments"):
            raise forms.ValidationError("Введите сообщение или прикрепите файл.")
        return cleaned


class EditMessageForm(forms.Form):
    text = forms.CharField(required=False, max_length=4096)

    def clean_text(self):
        return self.cleaned_data.get("text", "").strip()
