import re

from unidecode import unidecode


def slugfy(to_slugfy: str):
    normalized_name = unidecode(to_slugfy).lower()
    slug = re.sub(r'[^a-z0-9]+', '-', normalized_name)
    return slug.strip('-')
