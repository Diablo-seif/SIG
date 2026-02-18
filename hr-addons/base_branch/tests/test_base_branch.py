"""Integrated Tests for Branch"""

from odoo.tests.common import TransactionCase


# pylint: disable=too-many-instance-attributes
class TestBaseBranch(TransactionCase):
    """Integrated Tests"""

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the testing environment."""
        super(TestBaseBranch, self).setUp()
        # Usefull models
        self.ResBranch = self.env['res.branch']
        self.ResUsers = self.env['res.users']
        # Groups
        self.group_manage_branch = self.env.ref('base.group_partner_manager').id

        # USERS
        user_branch_values = {
            'name': 'Sample User Manage Branch',
            'login': 'manage_branch',
            'email': 'manage_branch@example.com',
            'groups_id': [(
                6, 0, [
                    self.group_manage_branch,
                    self.env.ref('base.group_user').id
                ]
            )]
        }
        self.user_manage_branch = self.ResUsers.create(user_branch_values)

    def test_01_create_branch(self):
        """Test Scenario: Create Branch."""
        values = {
            'name': 'Sample Branch #1',
            'code': 'SB1'
        }
        branch = self.ResBranch.with_user(
            self.user_manage_branch).create(values)
        self.assertTrue(branch, "test create branch done.")
