from django.utils import translation
from core.translations import get_translations_for_language

def language_processor(request):
    """Set language based on user preference."""
    if request.user.is_authenticated:
        try:
            lang = request.user.profile.preferred_language
        except:
            # User doesn't have a profile (e.g., admin user)
            lang = translation.get_language()
        translation.activate(lang)
        request.session['_language'] = lang
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
