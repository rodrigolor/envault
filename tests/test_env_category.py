import pytest
from pathlib import Path
from envault.env_category import CategoryManager, CategoryError


@pytest.fixture
def mgr(tmp_path: Path) -> CategoryManager:
    return CategoryManager(str(tmp_path))


class TestCategoryManager:
    def test_list_all_empty_initially(self, mgr: CategoryManager) -> None:
        assert mgr.list_all() == {}

    def test_list_categories_empty_initially(self, mgr: CategoryManager) -> None:
        assert mgr.list_categories() == []

    def test_assign_and_get(self, mgr: CategoryManager) -> None:
        mgr.assign("DB_HOST", "database")
        assert mgr.get_category("DB_HOST") == "database"

    def test_assign_persists_to_disk(self, tmp_path: Path) -> None:
        mgr1 = CategoryManager(str(tmp_path))
        mgr1.assign("API_KEY", "auth")
        mgr2 = CategoryManager(str(tmp_path))
        assert mgr2.get_category("API_KEY") == "auth"

    def test_assign_empty_key_raises(self, mgr: CategoryManager) -> None:
        with pytest.raises(CategoryError, match="Key must not be empty"):
            mgr.assign("", "network")

    def test_assign_empty_category_raises(self, mgr: CategoryManager) -> None:
        with pytest.raises(CategoryError, match="Category must not be empty"):
            mgr.assign("HOST", "")

    def test_unassign_removes_key(self, mgr: CategoryManager) -> None:
        mgr.assign("REDIS_URL", "cache")
        mgr.unassign("REDIS_URL")
        assert mgr.get_category("REDIS_URL") is None

    def test_unassign_unknown_key_raises(self, mgr: CategoryManager) -> None:
        with pytest.raises(CategoryError, match="has no category assigned"):
            mgr.unassign("MISSING_KEY")

    def test_list_by_category(self, mgr: CategoryManager) -> None:
        mgr.assign("DB_HOST", "database")
        mgr.assign("DB_PORT", "database")
        mgr.assign("API_KEY", "auth")
        result = mgr.list_by_category("database")
        assert sorted(result) == ["DB_HOST", "DB_PORT"]

    def test_list_by_category_empty(self, mgr: CategoryManager) -> None:
        assert mgr.list_by_category("nonexistent") == []

    def test_list_all_returns_mapping(self, mgr: CategoryManager) -> None:
        mgr.assign("X", "cat1")
        mgr.assign("Y", "cat2")
        assert mgr.list_all() == {"X": "cat1", "Y": "cat2"}

    def test_list_categories_sorted_unique(self, mgr: CategoryManager) -> None:
        mgr.assign("A", "zebra")
        mgr.assign("B", "apple")
        mgr.assign("C", "zebra")
        assert mgr.list_categories() == ["apple", "zebra"]

    def test_reassign_overwrites(self, mgr: CategoryManager) -> None:
        mgr.assign("PORT", "network")
        mgr.assign("PORT", "server")
        assert mgr.get_category("PORT") == "server"
