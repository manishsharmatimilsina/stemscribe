from django import template
import re
from core.translations import get_text

register = template.Library()

@register.filter
def split(value, sep):
    return value.split(sep)

@register.filter
def highlight_report(content, issues_json):
    """Highlight issue quotes in report content."""
    import json, html as html_module
    try:
        issues = json.loads(issues_json)
    except Exception:
        issues = []

    # Escape HTML first
    safe = html_module.escape(content)

    # Highlight each quoted phrase
    for i, issue in enumerate(issues):
        quote = html_module.escape(issue.get('quote', ''))
        if not quote:
            continue
        itype = issue.get('type', 'analysis')
        cls = {'understanding': 'mu', 'analysis': 'ma', 'communication': 'mc'}.get(itype, 'ma')
        issue_label = html_module.escape(issue.get('issue', ''))
        replacement = (
            f'<mark class="{cls}" onclick="scrollToFeedback({i})" '
            f'title="{issue_label}">{quote}</mark>'
        )
        safe = safe.replace(quote, replacement, 1)

    # Split into paragraphs, wrap each in <p>, detect section headers
    paragraphs = safe.split('\n\n')
    result = []
    section_names = ['Introduction', 'Method', 'Methods', 'Results', 'Discussion', 'Conclusion', 'Abstract']
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        clean = para.strip()
        if clean in section_names:
            result.append(f'<div class="report-section-title">{clean}</div>')
        else:
            para_html = para.replace('\n', '<br>')
            result.append(f'<p style="margin-bottom:.75rem;line-height:1.85">{para_html}</p>')
    return '\n'.join(result)

@register.filter
def tr(key, language='en'):
    """Translate a key to the specified language."""
    return get_text(key, language)
