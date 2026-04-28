from django.utils import translation
from django.conf import settings
from core.translations import get_translations_for_language

def language_processor(request):
    """Set language based on user preference."""
    if request.user.is_authenticated:
        lang = request.user.profile.preferred_language
        translation.activate(lang)
        request.session[settings.LANGUAGE_SESSION_KEY] = lang
    else:
        lang = translation.get_language()

    # Get translations for current language
    translations = get_translations_for_language(lang)

    return {
        'current_language': lang,
        'language_code': lang,
        'translations': translations,
        'tr': lambda key: translations.get(key, key),
    }
