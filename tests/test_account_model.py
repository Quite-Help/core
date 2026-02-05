from app.schema.account import Account, Role


class TestAccountModel:
    """Test Account model methods."""

    def test_account_roles_property_empty(self):
        """Test that roles property returns empty list when no roles."""
        account = Account(
            id=1, username="testuser", password="hashed", display_name="Test"
        )
        assert account.roles == []

    def test_account_roles_property_with_roles(self):
        """Test that roles property returns list of roles."""
        account = Account(
            id=1, username="testuser", password="hashed", display_name="Test"
        )
        account.add_role(Role.ADMIN)
        account.add_role(Role.SUPER_ADMIN)

        roles = account.roles
        assert len(roles) == 2
        assert Role.ADMIN in roles
        assert Role.SUPER_ADMIN in roles

    def test_add_role_adds_new_role(self):
        """Test that add_role adds a new role."""
        account = Account(
            id=1, username="testuser", password="hashed", display_name="Test"
        )
        account.add_role(Role.ADMIN)

        assert len(account.role_associations) == 1
        assert account.role_associations[0].role == Role.ADMIN
        assert Role.ADMIN in account.roles

    def test_add_role_does_not_duplicate(self):
        """Test that add_role does not add duplicate roles."""
        account = Account(
            id=1, username="testuser", password="hashed", display_name="Test"
        )
        account.add_role(Role.ADMIN)
        account.add_role(Role.ADMIN)

        assert len(account.role_associations) == 1
        assert len(account.roles) == 1

    def test_add_role_multiple_roles(self):
        """Test adding multiple different roles."""
        account = Account(
            id=1, username="testuser", password="hashed", display_name="Test"
        )
        account.add_role(Role.ADMIN)
        account.add_role(Role.SUPER_ADMIN)
        account.add_role(Role.SERVICE)

        assert len(account.role_associations) == 3
        assert Role.ADMIN in account.roles
        assert Role.SUPER_ADMIN in account.roles
        assert Role.SERVICE in account.roles

    def test_remove_role_removes_existing_role(self):
        """Test that remove_role removes an existing role."""
        account = Account(
            id=1, username="testuser", password="hashed", display_name="Test"
        )
        account.add_role(Role.ADMIN)
        account.add_role(Role.SUPER_ADMIN)

        account.remove_role(Role.ADMIN)

        assert len(account.role_associations) == 1
        assert Role.ADMIN not in account.roles
        assert Role.SUPER_ADMIN in account.roles

    def test_remove_role_no_effect_if_role_not_present(self):
        """Test that remove_role has no effect if role is not present."""
        account = Account(
            id=1, username="testuser", password="hashed", display_name="Test"
        )
        account.add_role(Role.ADMIN)
        initial_count = len(account.role_associations)

        account.remove_role(Role.SUPER_ADMIN)

        assert len(account.role_associations) == initial_count
        assert Role.ADMIN in account.roles

    def test_remove_role_all_roles(self):
        """Test removing all roles."""
        account = Account(
            id=1, username="testuser", password="hashed", display_name="Test"
        )
        account.add_role(Role.ADMIN)
        account.add_role(Role.SUPER_ADMIN)

        account.remove_role(Role.ADMIN)
        account.remove_role(Role.SUPER_ADMIN)

        assert len(account.role_associations) == 0
        assert account.roles == []
