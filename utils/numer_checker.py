import re 


UZ_PHONE_PATTERN = re.compile(
    r"^(?:\+998[- ]?)?\d{2}[- ]?\d{3}[- ]?\d{2}[- ]?\d{2}$"
)

def check_number(number : str) -> bool:
    sanitaized = number.replace('-', '').replace(' ', '').strip()
    return bool(UZ_PHONE_PATTERN.match(sanitaized))