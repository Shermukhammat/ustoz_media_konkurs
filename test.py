import re

UZ_PHONE_PATTERN = re.compile(
    r"^(?:\+998[- ]?)?\d{2}[- ]?\d{3}[- ]?\d{2}[- ]?\d{2}$"
)

tests = [
    '951739103',
    '+998951739103',
    '+998-95-173-91-03',
    '95 134 45 55',
    '33    123 44 76',
    '+998 97 777 77 77',
    '+998-71-200-00-00',
    '9517fgfgf3434433434'
]

for number in tests:
    sanitaized = number.replace('-', '').replace(' ', '').strip()
    print(f"{number}: {bool(UZ_PHONE_PATTERN.match(sanitaized))}")
