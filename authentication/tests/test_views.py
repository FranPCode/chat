from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

User = get_user_model()


def set_chromedriver_options():
    """Set the necessary options for the Chrome WebDriver to function correctly."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    return driver


class WrappedElement:
    """Wrap an selenium web element and automaticly handle de exceptions."""

    def __init__(self, driver, locator, wait_time=5):
        self.driver = driver
        self.locator = locator
        self.element = None
        self.wait_time = wait_time

    def find(self):
        """
        Find the element in the DOM.
        Same behavior of selenium find()
        """
        self.element = WebDriverWait(
            self.driver,
            self.wait_time
        ).until(
            EC.presence_of_element_located(self.locator)
        )

    def click(self):
        """
        Click the element. Same behavior of selenium click().
        Handle the exception if raised.
        """
        try:
            self.element.click()
        except StaleElementReferenceException:
            self.find()
            self.element.click()

    def send_keys(self, string: str):
        """
        Send keys to the element. Same behavior of selenium send_keys().
        Handle the exception if raised.
        """
        try:
            self.element.send_keys(string)
        except StaleElementReferenceException:
            self.find()
            self.element.send_keys(string)

    def clear(self):
        """
        Clear the element input. Same behavior of selenium clear().
        Handle the exception if raised.
        """
        try:
            self.element.clear()
        except StaleElementReferenceException:
            self.find()
            self.element.clear()


class LoginViewTest(StaticLiveServerTestCase):
    """End to end test for login view."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testusername',
            email='test@email.com',
            password='testpassword123'
        )
        self.driver = set_chromedriver_options()

    def tearDown(self):
        self.driver.quit()

    def test_login(self):
        """Test the correct behavior of user login."""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")

        username_input = WrappedElement(self.driver, (By.NAME, 'username'))
        password_input = WrappedElement(self.driver, (By.NAME, 'password'))
        login_button = WrappedElement(self.driver, (By.ID, 'login-button'))

        username_input.find()
        password_input.find()
        login_button.find()

        username_input.send_keys('wrongusername')
        password_input.send_keys('wrongpassword')
        login_button.click()

        error_message = self.driver.find_element(
            By.CLASS_NAME, value='error-message')

        self.assertTrue(error_message)

        username_input.clear()
        password_input.clear()

        username_input.send_keys(self.user.username)
        password_input.send_keys('wrongpassword')
        login_button.click()

        self.assertEqual(self.driver.title, 'Login')

        username_input.clear()
        password_input.clear()

        username_input.send_keys(self.user.username)
        password_input.send_keys('testpassword123')
        login_button.click()

        self.assertNotEqual(self.driver.title, 'Login')


class RegisterViewTest(StaticLiveServerTestCase):
    """End to end test for register view."""

    def setUp(self):
        self.user = {
            'username': 'testusername',
            'email': 'test@email.com',
            'password': 'testpassword123',
        }
        self.driver = set_chromedriver_options()

    def tearDown(self):
        self.driver.quit()

    def test_register(self):
        """Test the correct behavior of user register."""
        self.driver.get(f"{self.live_server_url}{reverse('register')}")

        username_input = WrappedElement(self.driver, (By.NAME, 'username'))
        email_input = WrappedElement(self.driver, (By.NAME, 'email'))
        password_input = WrappedElement(self.driver, (By.NAME, 'password1'))
        password2_input = WrappedElement(self.driver, (By.NAME, 'password2'))
        register_button = WrappedElement(
            self.driver, (By.ID, 'register-button'))

        username_input.find()
        email_input.find()
        password_input.find()
        password2_input.find()
        register_button.find()

        username_input.send_keys('wrongusername')
        register_button.click()
        self.assertEqual(self.driver.title, 'Register')

        username_input.clear()

        username_input.send_keys(self.user['username'])
        email_input.send_keys('wrongpassword')
        register_button.click()
        self.assertEqual(self.driver.title, 'Register')

        username_input.clear()
        email_input.clear()

        username_input.send_keys(self.user['username'])
        email_input.send_keys(self.user['email'])
        password_input.send_keys(self.user['password'])
        register_button.click()
        self.assertEqual(self.driver.title, 'Register')

        username_input.clear()
        email_input.clear()
        password_input.clear()

        username_input.send_keys(self.user['username'])
        email_input.send_keys(self.user['email'])
        password_input.send_keys(self.user['password'])
        password2_input.send_keys('nosamepassword')
        register_button.click()
        self.assertEqual(self.driver.title, 'Register')

        error_message = self.driver.find_element(
            By.CLASS_NAME, value='error-message')
        self.assertTrue(error_message)

        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-message'))
        )

        username_input.clear()
        email_input.clear()
        password_input.clear()
        password2_input.clear()

        username_input.send_keys(self.user['username'])
        email_input.send_keys(self.user['email'])
        password_input.send_keys(self.user['password'])
        password2_input.send_keys(self.user['password'])
        register_button.click()
        self.assertEqual(self.driver.title, 'Login')
