import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartneighbour_api.settings')

import django
django.setup()

from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404

print("=" * 60)
print("  URL PATTERN TEST")
print("=" * 60)
print()

# Test reverse lookup
try:
    url = reverse('login')
    print(f"✓ 'login' reverse URL: {url}")
except:
    print("✗ Failed to reverse 'login'")

# Test resolve
test_paths = [
    '/api/auth/login/',
    '/auth/login/',
    'api/auth/login/',
    'auth/login/',
]

for path in test_paths:
    try:
        match = resolve(path)
        print(f"✓ '{path}' → {match.func.__name__}")
    except Resolver404:
        print(f"✗ '{path}' → 404 Not Found")
    except Exception as e:
        print(f"✗ '{path}' → Error: {e}")

print()
print("=" * 60)
