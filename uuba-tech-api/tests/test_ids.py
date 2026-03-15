from app.utils.ids import generate_id


def test_generate_id_with_prefix():
    result = generate_id("fat")
    assert result.startswith("fat_")
    assert len(result) == 4 + 12  # prefix_ + 12 chars


def test_generate_id_unique():
    ids = {generate_id("cli") for _ in range(100)}
    assert len(ids) == 100
