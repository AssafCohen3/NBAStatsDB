import json
from typing import Dict

# noinspection PyPackageRequirements
import i18n

i18n.set('file_format', 'json')
i18n.set('filename_format', '{locale}.{format}')
i18n.set('skip_locale_root_data', True)
i18n.load_path.append('dbmanager/locale/')


def gettext(path: str, **kwargs) -> str:
    return i18n.t(path, **kwargs)


def gettext_marker(path: str):
    return path


def set_locale(new_locale: str):
    i18n.set('locale', new_locale)


def get_available_locales() -> Dict[str, str]:
    return i18n.get('available_locales')


def get_default_locale() -> str:
    return i18n.get('fallback')


class TranslatableField:
    def __init__(self, translations: Dict[str, str], fallback_locale='en'):
        self.translations = translations
        self.fallback_locale = fallback_locale

    def get_value(self):
        current_locale = i18n.get('locale')
        if current_locale in self.translations:
            return self.translations[current_locale]
        if self.fallback_locale in self.translations:
            return self.translations[self.fallback_locale]
        return ''

    def get_translations(self) -> Dict[str, str]:
        return self.translations


def create_translatable_from_json(json_object: str) -> TranslatableField:
    return TranslatableField(json.loads(json_object))
