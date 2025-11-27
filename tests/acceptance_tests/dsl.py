import time
from typing import Dict

from tests.acceptance_tests.driver import Driver


class Dsl:

    DEFAULT_REGISTER_NAME = "Register of Things"
    DEFAULT_ENTRY_NAME = "An entry"

    def __init__(self, driver: Driver):
        self.driver = driver
        self.aliases: Dict[str, str] = {}

    def _encode_alias(self, name):
        if name == "":
            return ""
        if name not in self.aliases:
            self.aliases[name] = name + str(round(time.time() * 1000))
        return self.aliases[name]

    def _decode_alias(self, name):
        if name in self.aliases:
            return self.aliases[name]
        else:
            return ""

    def setup(self):
        self.driver.setup()

    def tear_down(self):
        self.driver.tear_down()

    def ensure_existing_register(self, name=DEFAULT_REGISTER_NAME):
        self.create_new_register(name, 100)
        self.confirm_register_created(name)

    def create_new_register(self, name=DEFAULT_REGISTER_NAME, price=100):
        self.driver.create_new_register(self._encode_alias(name), price)

    def confirm_register_created(self, name=DEFAULT_REGISTER_NAME):
        self.driver.confirm_register_created(self._decode_alias(name))

    def confirm_name_required_validation_error(self):
        self.driver.confirm_name_required_validation_error()

    def confirm_name_already_exists_validation_error(self):
        self.driver.confirm_name_already_exists_validation_error()

    def confirm_can_view_register(self, name=DEFAULT_REGISTER_NAME):
        self.driver.confirm_can_view_register(self._decode_alias(name))

    def update_existing_register(self, current_name=DEFAULT_REGISTER_NAME, new_name=""):
        current_name_alias = self._encode_alias(current_name)
        new_name_alias = self._encode_alias(new_name)
        self.driver.update_existing_register(current_name_alias, new_name_alias, 200)

    def confirm_register_updated(self, old_name=DEFAULT_REGISTER_NAME, new_name=""):
        old_name_alias = self._decode_alias(old_name)
        new_name_alias = self._decode_alias(new_name)
        self.driver.confirm_register_updated(old_name_alias, new_name_alias)

    def delete_existing_register(self, name=DEFAULT_REGISTER_NAME):
        alias = self._encode_alias(name)
        self.driver.delete_existing_register(alias)

    def confirm_deletion_requires_confirmation(self, name=DEFAULT_REGISTER_NAME):
        alias = self._decode_alias(name)
        self.driver.confirm_deletion_requires_confirmation(alias)

    def cancel_register_deletion(self, name=DEFAULT_REGISTER_NAME):
        alias = self._decode_alias(name)
        self.driver.cancel_register_deletion(alias)

    def confirm_register_deletion(self, name=DEFAULT_REGISTER_NAME):
        alias = self._decode_alias(name)
        self.driver.confirm_register_deletion(alias)

    def confirm_register_deleted(self, name=DEFAULT_REGISTER_NAME):
        alias = self._decode_alias(name)
        self.driver.confirm_register_deleted(alias)

    def confirm_register_exists(self, name=DEFAULT_REGISTER_NAME):
        alias = self._decode_alias(name)
        self.driver.confirm_register_exists(alias)

    def ensure_existing_entry(self, register=DEFAULT_REGISTER_NAME, entry_name=DEFAULT_ENTRY_NAME):
        self.add_entry_to_register(register=register, entry_name=entry_name)
        self.confirm_entry_added(register=register, entry_name=entry_name)

    def add_entry_to_register(self, register=DEFAULT_REGISTER_NAME, entry_name=DEFAULT_ENTRY_NAME):
        self.driver.add_entry_to_register(
            register=self._encode_alias(register), entry_name=self._encode_alias(entry_name)
        )

    def confirm_entry_added(self, register=DEFAULT_REGISTER_NAME, entry_name=DEFAULT_ENTRY_NAME):
        self.driver.confirm_entry_added(
            register=self._decode_alias(register), entry_name=self._decode_alias(entry_name)
        )

    def confirm_can_view_entry(self, register=DEFAULT_REGISTER_NAME, entry_name=DEFAULT_ENTRY_NAME):
        self.driver.confirm_can_view_entry(
            register=self._encode_alias(register), entry_name=self._encode_alias(entry_name)
        )
