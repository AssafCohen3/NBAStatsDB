import i18n

i18n.set('file_format', 'json')
i18n.set('filename_format', '{locale}.{format}')
i18n.set('skip_locale_root_data', True)
i18n.load_path.append('dbmanager/locale/')


def gettext(path: str, **kwargs) -> str:
    return i18n.t(path, **kwargs)


def set_locale(new_locale: str):
    i18n.set('locale', new_locale)
