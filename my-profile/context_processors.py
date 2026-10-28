"""Template context shared by every page: profile details and which nav item is active."""

SITE = {
    'name': 'William Woo',
    'tagline': 'Senior Project/Program Manager | Full Stack & Cloud Proficient',
    'email': 'williamwoo@shin-woo.com',
    'phone': '415-470-0457',
    'linkedin': 'https://www.linkedin.com/in/williamwoo99/',
    'github': 'https://github.com/billywoo99',
}

# URL names that belong under a different top-level nav item.
_PUBLIC_ALIASES = {'profile': 'home', 'case': 'case-studies'}


def site(request):
    match = getattr(request, 'resolver_match', None)
    name = (match.url_name or '') if match else ''
    parts = name.split('-')
    if parts[0] == 'jscc':
        section = parts[1] if len(parts) > 1 else 'dashboard'
        return {'SITE': SITE, 'nav_active': '', 'jscc_active': section}
    section = _PUBLIC_ALIASES.get(parts[0], parts[0])
    return {'SITE': SITE, 'nav_active': section, 'jscc_active': ''}
