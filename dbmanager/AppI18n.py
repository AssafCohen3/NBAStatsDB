from __future__ import annotations
import json
import typing
from abc import ABC, abstractmethod
from typing import Dict, Type

# noinspection PyPackageRequirements
import i18n

from dbmanager.utils import get_application_path

if typing.TYPE_CHECKING:
    from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc

i18n.set('file_format', 'json')
i18n.set('filename_format', '{locale}.{format}')
i18n.set('skip_locale_root_data', True)
i18n.load_path.append(get_application_path() / 'dbmanager/locale/')


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


class TranslatableField(ABC):
    @abstractmethod
    def get_value(self) -> str:
        pass


class TranslatableFieldFromDict(TranslatableField):
    def __init__(self, translations: Dict[str, str], fallback_locale='en'):
        self.translations = translations
        self.fallback_locale = fallback_locale

    def get_value(self):
        current_locale = i18n.get('locale')
        if self.translations.get(current_locale):
            return self.translations[current_locale]
        if self.translations.get(self.fallback_locale):
            return self.translations[self.fallback_locale]
        return ''

    def get_translations(self) -> Dict[str, str]:
        return self.translations


def create_translatable_from_json(json_object: str) -> TranslatableFieldFromDict:
    return TranslatableFieldFromDict(json.loads(json_object))


class TranslatableFieldFromAction(TranslatableField):
    def __init__(self, action_spec: Type[ActionSpecificationAbc]):
        self.action_spec = action_spec

    def get_value(self):
        return self.action_spec.get_action_title()


class TranslatableFieldFromPath(TranslatableField):
    def __init__(self, path: str):
        self.path = path

    def get_value(self):
        return gettext(self.path)
