import pytest

from contaxy.utils import id_utils


@pytest.mark.parametrize(
    "input_str,max_length,min_length,expected_id",
    [("test", 8, 4, "test")],
)
def test_generate_readable_id(
    input_str: str, max_length: int, min_length: int, expected_id: str
) -> None:
    result = id_utils.generate_readable_id(
        input_str, max_length=max_length, min_length=min_length
    )
    assert result == expected_id


def test_generate_short_uuid() -> None:
    # Short UUID should have a length of 25
    assert len(id_utils.generate_short_uuid()) == 25
    # All uuids should be different
    assert id_utils.generate_short_uuid() != id_utils.generate_short_uuid()


def test_generate_token() -> None:
    # Should return a token with the given length
    for token_length in range(1, 40):
        assert len(id_utils.generate_token(token_length)) == token_length

    # All tokens should be different
    assert id_utils.generate_token(40) != id_utils.generate_token(40)


def test_get_project_resource_prefix() -> None:
    from contaxy.config import settings

    assert (
        id_utils.get_project_resource_prefix("my-project")
        == settings.SYSTEM_NAMESPACE + "-p-my-project"
    )
