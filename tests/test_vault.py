"""Tests for vault module."""

import pytest
import tempfile
from pathlib import Path

from envault.vault import Vault
from envault.storage import LocalFileStorage


class TestVault:
    """Test cases for Vault class."""

    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        yield LocalFileStorage(temp_path)
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    def test_set_and_get_variable(self, temp_storage):
        """Test setting and getting a single variable."""
        vault = Vault("test_password", temp_storage)
        vault.set("API_KEY", "secret123")
        
        assert vault.get("API_KEY") == "secret123"

    def test_get_nonexistent_variable(self, temp_storage):
        """Test getting a variable that doesn't exist."""
        vault = Vault("test_password", temp_storage)
        assert vault.get("NONEXISTENT") is None

    def test_get_all_variables(self, temp_storage):
        """Test getting all variables."""
        vault = Vault("test_password", temp_storage)
        vault.set("API_KEY", "secret123")
        vault.set("DB_PASSWORD", "dbpass456")
        
        all_vars = vault.get_all()
        assert all_vars == {"API_KEY": "secret123", "DB_PASSWORD": "dbpass456"}

    def test_delete_variable(self, temp_storage):
        """Test deleting a variable."""
        vault = Vault("test_password", temp_storage)
        vault.set("API_KEY", "secret123")
        vault.set("DB_PASSWORD", "dbpass456")
        
        result = vault.delete("API_KEY")
        assert result is True
        assert vault.get("API_KEY") is None
        assert vault.get("DB_PASSWORD") == "dbpass456"

    def test_delete_nonexistent_variable(self, temp_storage):
        """Test deleting a variable that doesn't exist."""
        vault = Vault("test_password", temp_storage)
        result = vault.delete("NONEXISTENT")
        assert result is False

    def test_persistence_across_instances(self, temp_storage):
        """Test that data persists across vault instances."""
        vault1 = Vault("test_password", temp_storage)
        vault1.set("API_KEY", "secret123")
        
        vault2 = Vault("test_password", temp_storage)
        assert vault2.get("API_KEY") == "secret123"

    def test_wrong_password_fails(self, temp_storage):
        """Test that wrong password cannot decrypt data."""
        vault1 = Vault("correct_password", temp_storage)
        vault1.set("API_KEY", "secret123")
        
        vault2 = Vault("wrong_password", temp_storage)
        with pytest.raises(Exception):
            vault2.get("API_KEY")

    def test_clear_vault(self, temp_storage):
        """Test clearing all vault data."""
        vault = Vault("test_password", temp_storage)
        vault.set("API_KEY", "secret123")
        vault.clear()
        
        assert vault.get_all() is None

    def test_update_existing_variable(self, temp_storage):
        """Test updating an existing variable."""
        vault = Vault("test_password", temp_storage)
        vault.set("API_KEY", "old_value")
        vault.set("API_KEY", "new_value")
        
        assert vault.get("API_KEY") == "new_value"
