def find_login_fields(page):
    """Erweiterte Suche mit Shadow DOM-Unterstützung für Proton."""
    url = page.url

    # 1. Proton-spezifische Selectoren (mit Shadow DOM)
    if "proton.me" in url or "protonmail.com" in url:
        try:
            # Shadow DOM durchdringen mit >> (Playwright-Syntax)
            username_field = page.locator(
                "proton-login >> input[data-testid='username']"
            ).first
            password_field = page.locator(
                "proton-login >> input[data-testid='password']"
            ).first
            if username_field.count() > 0 and password_field.count() > 0:
                return username_field, password_field
        except:
            pass

    # 2. Standard-Suche für andere Websites
    username_selectors = [
        'input[type="email"]',
        'input[name="email"]',
        'input[name="username"]',
        'input[id="email"]',
        'input[id="username"]',
        'input[placeholder*="email" i]',
        'input[placeholder*="user" i]',
        'input[aria-label*="email" i]',
        'input[aria-label*="user" i]',
    ]

    password_selectors = [
        'input[type="password"]',
        'input[name="password"]',
        'input[id="password"]',
        'input[placeholder*="passwort" i]',
        'input[placeholder*="password" i]',
        'input[aria-label*="passwort" i]',
        'input[aria-label*="password" i]',
    ]

    # Suche Username-Feld
    username_field = None
    for selector in username_selectors:
        try:
            field = page.locator(selector).first
            if field.count() > 0:
                username_field = field
                break
        except:
            continue

    # Suche Passwort-Feld
    password_field = None
    for selector in password_selectors:
        try:
            field = page.locator(selector).first
            if field.count() > 0:
                password_field = field
                break
        except:
            continue

    return username_field, password_field
