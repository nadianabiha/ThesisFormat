from django.contrib import admin
from django.test import TestCase

from .models import MasterRule


class MasterRuleAdminTest(TestCase):
    def test_master_rule_is_registered_in_admin(self):
        self.assertIn(MasterRule, admin.site._registry)
