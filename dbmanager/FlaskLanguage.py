"""
    inspired by https://github.com/rclement/flask-language
"""
from typing import Dict

import i18n
from flask import request

from dbmanager.AppI18n import set_locale


class Language(object):
    def __init__(self, app):
        self._allowed_languages = app.config['LANGUAGES']
        self._default_language = app.config['DEFAULT_LANGUAGE']
        self.init_app(app)

    def init_app(self, app):
        app.before_request(self._before_request)
        i18n.set('available_locales', list(self.get_available_languages().keys()))
        i18n.set('fallback', self._default_language)
        return self

    def get_available_languages(self) -> Dict[str, str]:
        return self._allowed_languages

    def _before_request(self):
        """
        Retrieve the current language using the following policy:
            1. Try to extract the language cookie
            2. If no language cookie is found, try to find a match between
               `request.accept_languages` and :class:`allowed_languages`
            3. If no match is found, use the :class:`default_language`
        Afterwards, the `current_language` will be available.
        """
        allowed_languages = self._allowed_languages
        default_language = self._default_language
        request_lang = request.accept_languages.best_match(allowed_languages)
        language = request_lang or default_language
        set_locale(language)
