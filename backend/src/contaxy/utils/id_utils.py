"""Utilities for generating IDs, tokens, and hashes."""

import hashlib
import math
import re
import secrets
import string
from email.utils import parseaddr
from typing import List, Optional, Tuple

import shortuuid
from slugify import slugify

from contaxy.config import settings

_PROJECT_ID_SEPERATOR = "-p-"
_PROJECT_NAME_TO_ID_REGEX = re.compile(r"^projects/([^/:\s]+)$")
_USER_NAME_TO_ID_REGEX = re.compile(r"^users/([^/:\s]+)$")
_SERVICE_RESOURCE_REGEX = re.compile(r"^projects/([^/:\s]+)/services/([^/:\s]+)")


def is_email(text: str) -> bool:
    """Returns `True` if the given `text` has the format of an email address."""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", text):
        return False
    return "@" in parseaddr(text)[1]


def extract_user_id_from_resource_name(user_resource_name: str) -> str:
    """Extract the user id from a provided resource name.

    Raises:
        ValueError: If the `user_resource_name` is not valid.
    """
    match = re.match(_USER_NAME_TO_ID_REGEX, user_resource_name)
    if match:
        return match[1]
    else:
        raise ValueError(
            f"The provided user_resource_name is not valid: {user_resource_name}"
        )


def extract_project_id_from_resource_name(project_resource_name: str) -> str:
    """Extract the project id from a provided resource name.

    Raises:
        ValueError: If the `project_resource_name` is not valid.
    """
    match = re.match(_PROJECT_NAME_TO_ID_REGEX, project_resource_name)
    if match:
        return match[1]
    else:
        raise ValueError(
            f"The provided project_resource_name is not valid: {project_resource_name}"
        )


def extract_ids_from_service_resource_name(
    service_resource_name: str,
) -> Tuple[str, str]:
    """Extract the project id and service id from a service resource name.

    Args:
        service_resource_name (str): The service resource name (e.g. /projects/project-id/services/service-id)

    Returns:
        Tuple[str, str]: The project id and service id contained in the resource name
    """
    match = _SERVICE_RESOURCE_REGEX.match(service_resource_name)
    if match is None:
        raise ValueError(
            f"Resource name {service_resource_name} is not a service resource!"
        )
    groups = match.groups()
    return groups[0], groups[1]


def get_project_resource_prefix(project_id: str) -> str:
    """Creates a prefix usable to construct IDs for project resources.

    The resource prefix is based on the system namespace and project ID.
    """
    return settings.SYSTEM_NAMESPACE + _PROJECT_ID_SEPERATOR + project_id


def hash_str(input_str: str, length: Optional[int] = None) -> str:
    """Generates a hash with a variable lenght from an abritary text.

    Args:
        input_str (str): Text to hash.
        length (Optional[int], optional): The length of the generated hash. A shorter hash will result in more possible collusions.
    """
    # Alternatives:
    # hashlib.shake_128(input_str.encode('UTF-8')).hexdigest(length)
    # hashlib.md5, hashlib.sha512
    # Base64 encode? base64.urlsafe_b64encode(hasher.digest()[:10])
    # h.digest().encode('base64')[:6]
    hashed_str = hashlib.sha1(input_str.encode("UTF-8")).hexdigest()

    if length:
        if length > len(hashed_str):
            raise ValueError(
                "The length cannot be set to be more then " + str(len(hashed_str))
            )
        hashed_str = hashed_str[:length]

    return hashed_str


def generate_token(length: int) -> str:
    """Generates a random token with the specified length."""
    # secrets.token_hex returns all bytes as hex (2 bytes per character)
    # Alternative: secrets.token_urlsafe(length) -> base64 encoded token
    return str(secrets.token_hex(math.ceil(length / 2)))[:length]


def generate_short_uuid() -> str:
    """Generates a short - 25 chars - UUID by using all ascii letters and digits."""
    shortuuid.set_alphabet(string.ascii_letters.lower() + string.digits)
    return str(shortuuid.uuid())


def generate_readable_id(
    input_str: str,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
    max_hash_suffix_length: Optional[int] = None,
    separator: str = "-",
    stopwords: Optional[List[str]] = None,
) -> str:
    """Generates a human- and URL-friendly ID from arbritary text.

    Args:
        input_str (str): Text to use for ID generation.
        max_length (Optional[int], optional): Maximal length of the ID. Defaults to `None`.
        min_length (Optional[int], optional): Minimal length of the ID. The generated ID will be filled with a suffix based on its hash. Defaults to `None`.
        suffix (Optional[str], optional): Suffix to add to the generated ID. Defaults to `None`.
        prefix (Optional[str], optional): Prefix to add the the generated ID. Defaults to `None`.
        max_hash_suffix_length (Optional[int], optional): Number of chars to append to the generated ID to allow generating unique IDs with a max lengths. Defaults to `None`.
        separator (str, optional): Seperator to use for replacing whitespaces. Defaults to `-`.
        stopwords (Optional[List[str]], optional): List of stopwords to ignore in the generated ID. Defaults to `None`.

    Raises:
        ValueError: A a function parameter has an inappropriate value.

    Returns:
        str: The generated ID human- and URL-friendly ID.
    """
    if not max_length:
        # Set max_length to the length of the input text if not provided
        max_length = len(input_str)

    if max_length <= 0:
        raise ValueError("The max_length should be bigger than 0.")

    adapted_max_length = max_length

    if suffix:
        adapted_max_length = max_length - len(suffix)

    if prefix:
        adapted_max_length = max_length - len(prefix)

    if adapted_max_length <= 0:
        raise ValueError("The max_length should be more than the suffix and/or prefix.")

    if max_hash_suffix_length:
        if max_length < max_hash_suffix_length:
            raise ValueError(
                "The max_length should not be smaller than the hash suffix."
            )
        adapted_max_length = 0

    if min_length and min_length > max_length:
        raise ValueError("The min_length should not be bigger than max_length.")

    if not stopwords:
        stopwords = []

    generated_id = slugify(
        input_str,
        max_length=adapted_max_length,
        stopwords=stopwords,
        separator=separator,
        entities=False,
        decimal=False,
        hexadecimal=False,
        lowercase=True,
        word_boundary=False,
    )

    if max_hash_suffix_length and len(generated_id) > max_length:
        if max_length <= (max_hash_suffix_length + len(separator)):
            # Only return the hash
            return hash_str(generated_id, length=max_hash_suffix_length)[:max_length]

        # shorten
        shortened_id = generated_id[: max_length - max_hash_suffix_length]
        if not shortened_id.endswith(separator):
            # Append minus
            shortened_id = shortened_id[: -len(separator)] + separator

        generated_id = shortened_id + hash_str(
            generated_id, length=max_hash_suffix_length
        )

    if suffix:
        generated_id = generated_id + suffix

    if prefix:
        generated_id = prefix + generated_id

    # Slugify again to include suffix/prefix
    generated_id = slugify(
        generated_id,
        max_length=max_length,
        separator=separator,
        stopwords=stopwords,
        entities=False,
        decimal=False,
        hexadecimal=False,
        lowercase=True,
        word_boundary=False,
    )

    if min_length and len(generated_id) < min_length:
        generated_id += hash_str(generated_id, length=min_length - len(generated_id))

    return generated_id
