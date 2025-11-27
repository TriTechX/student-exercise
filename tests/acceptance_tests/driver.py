from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Driver:

    def __init__(self, base_url):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--ignore-certificate-errors")
        self.browser = webdriver.Chrome(options=options)
        self.base_url = base_url

    def _navigate_to_registers(self):
        self._find_and_click(By.LINK_TEXT, "Registers")

        register_heading = self.browser.find_element(By.TAG_NAME, "h1")
        assert register_heading.text == "Registers"

    def _view_register(self, name):
        self._find_and_click(By.LINK_TEXT, name)

        page_heading = self.browser.find_element(By.TAG_NAME, "h1")
        assert page_heading.text == name

    def _view_entry(self, entry_name):
        self._find_and_click(By.LINK_TEXT, entry_name)

        page_heading = self.browser.find_element(By.TAG_NAME, "h1")
        assert page_heading.text == entry_name

    def _find_and_click(self, by: ByType, locator: str):
        element = WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((by, locator)))
        element.click()
        try:
            WebDriverWait(self.browser, 5).until(EC.staleness_of(element))
        except WebDriverException:
            # If this fails, just continue as likely caused by the speed the page reloads
            pass

    def _confirm_page_has_errors(self):
        WebDriverWait(self.browser, 5).until(EC.title_contains("Error:"))
        assert self.browser.title.startswith("Error: ")

        error_heading = self.browser.find_element(By.XPATH, "//h2[contains(text(),'There is a problem')]")
        assert error_heading is not None, "Error heading not found"

    def setup(self):
        self.browser.get(self.base_url)
        assert self.browser.title.endswith("GOV.UK")

    def tear_down(self):
        self.browser.quit()

    def create_new_register(self, name, price):
        self._navigate_to_registers()

        self._find_and_click(By.LINK_TEXT, "Create new register")

        heading = self.browser.find_element(By.TAG_NAME, "h1")
        assert heading.text == "Create new register"

        name_field = self.browser.find_element(By.NAME, "name")
        name_field.send_keys(name)

        price_field = self.browser.find_element(By.NAME, "price")
        price_field.send_keys(price)

        self._find_and_click(By.NAME, "submit")

    def confirm_name_required_validation_error(self):
        self._confirm_page_has_errors()

        error_message = self.browser.find_element(By.XPATH, "//a[text()='Enter a name']")
        assert error_message is not None, "Error message not found"

    def confirm_name_already_exists_validation_error(self):
        self._confirm_page_has_errors()

        error_message = self.browser.find_element(By.XPATH, "//a[text()='Name already in use']")
        assert error_message is not None, "Error message not found"

    def confirm_register_created(self, name):
        success_message = self.browser.find_element(By.XPATH, "//*[contains(text(),'Successfully created register')]")
        assert success_message is not None, "Success message not found"

        self.confirm_register_exists(name)

    def confirm_register_exists(self, name):
        self._navigate_to_registers()

        existing_register = self.browser.find_element(By.XPATH, f"//*[contains(text(),'{name}')]")
        assert existing_register is not None, "Register not found"

    def confirm_can_view_register(self, name):
        self._navigate_to_registers()
        self._view_register(name)

    def update_existing_register(self, name, new_name, price):
        self._navigate_to_registers()
        self._view_register(name)

        self._find_and_click(By.LINK_TEXT, "Edit register")

        name_field = self.browser.find_element(By.NAME, "name")
        assert name_field.get_attribute("value") == name

        name_field.clear()
        name_field.send_keys(new_name)

        price_field = self.browser.find_element(By.NAME, "price")
        # assert price_field.get_attribute("value") == price

        price_field.clear()
        price_field.send_keys(price)

        self._find_and_click(By.NAME, "submit")

    def confirm_register_updated(self, old_name, new_name):
        updated_message = self.browser.find_element(By.XPATH, "//*[contains(text(),'Successfully updated register')]")
        assert updated_message is not None, "Updated message not found"

        self._navigate_to_registers()

        try:
            self.browser.find_element(By.XPATH, f"//*[contains(text(), '{old_name}')]")
            raise AssertionError("Register with old name still exists")
        except NoSuchElementException:
            pass

        new_register = self.browser.find_element(By.XPATH, f"//*[contains(text(), '{new_name}')]")
        assert new_register is not None, "Register with new name not found"

    def delete_existing_register(self, name):
        self._navigate_to_registers()
        self._view_register(name)

        self._find_and_click(By.LINK_TEXT, "Delete register")

    def confirm_deletion_requires_confirmation(self, name):
        confirmation_prompt = self.browser.find_element(
            By.XPATH,
            f"//*[contains(text(),'Are you sure you want to delete the {name} register?')]",
        )
        assert confirmation_prompt is not None, "Confirmation prompt not found"

    def cancel_register_deletion(self, name):
        self._find_and_click(By.LINK_TEXT, "Cancel")

    def confirm_register_deletion(self, alias):
        confirm_checkbox = self.browser.find_element(By.NAME, "confirm")
        confirm_checkbox.click()

        self._find_and_click(By.NAME, "submit")

    def confirm_register_deleted(self, name):
        deleted_message = self.browser.find_element(By.XPATH, "//*[contains(text(),'Successfully deleted register')]")
        assert deleted_message is not None, "Deleted message not found"

        self._navigate_to_registers()

        try:
            self.browser.find_element(By.XPATH, f"//*[contains(text(), '{name}')]")
            raise AssertionError("Deleted register still exists")
        except NoSuchElementException:
            pass

    def add_entry_to_register(self, register, entry_name):
        self._navigate_to_registers()
        self._view_register(register)

        self._find_and_click(By.LINK_TEXT, "Add new entry")

        heading = self.browser.find_element(By.TAG_NAME, "h1")
        assert heading.text == "Add new entry"

        name_field = self.browser.find_element(By.NAME, "name")
        name_field.send_keys(entry_name)

        self._find_and_click(By.NAME, "submit")

    def confirm_entry_added(self, register, entry_name):
        added_message = self.browser.find_element(
            By.XPATH, "//*[contains(text(),'Successfully added entry to register')]"
        )
        assert added_message is not None, "Success message not found"

        self.confirm_entry_exists(register, entry_name)

    def confirm_entry_exists(self, register, entry_name):
        self._navigate_to_registers()
        self._view_register(register)

        existing_entry = self.browser.find_element(By.XPATH, f"//*[contains(text(),'{entry_name}')]")
        assert existing_entry is not None, "Entry not found in register"

    def confirm_can_view_entry(self, register, entry_name):
        self._navigate_to_registers()
        self._view_register(register)
        self._view_entry(entry_name)
