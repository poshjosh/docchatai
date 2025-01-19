import hashlib
import os
import re
import uuid

_non_alpha_numeric_pattern = re.compile('[^A-Za-z0-9_-]+')

def safe_unique_key(name: str, discriminator: str) -> str:
    # Keep these to provide a glimpse of the which chat model and file was used.
    formatted_discr = _non_alpha_numeric_pattern.sub('_', discriminator[:32])
    formatted_name = _non_alpha_numeric_pattern.sub('_', os.path.basename(name)[-32:])
    # Use a hash to keep the name short and unique.
    hash_hex = hashlib.sha256(f'{discriminator}{name}'.encode()).hexdigest()
    return f'{formatted_discr}_{formatted_name}_{hash_hex}'

def safe_unique_path_name(path: str, discriminator: str = str(uuid.uuid4().hex)) -> str:
    formatted_discr = _non_alpha_numeric_pattern.sub('_', discriminator[:64])
    name, ext = os.path.splitext(path)
    formatted_name = _non_alpha_numeric_pattern.sub('_', os.path.basename(name)[-64:])
    return f'{formatted_discr}_{formatted_name}{ext}'
