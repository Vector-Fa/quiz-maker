import re
import unidecode


def slugify(value: str) -> str:
    text = unidecode.unidecode(value).lower()
    return re.sub(r"[\W_]+", "-", text)
