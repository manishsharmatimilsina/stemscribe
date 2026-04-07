from django import template
import re

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

    # Section headers
    for section in ['Introduction', 'Method', 'Methods', 'Results', 'Discussion', 'Conclusion']:
        safe = re.sub(
            rf'^{section}$',
            f'<div class="report-section-title">{section}</div>',
            safe, flags=re.MULTILINE
        )

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

    safe = safe.replace('\n\n', '<br><br>').replace('\n', ' ')
    return safe
