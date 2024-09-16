"""
Tests for room views.
"""
import time
from channels.testing import ChannelsLiveServerTestCase

from django.contrib.auth import get_user_model

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from rooms.models import Message

User = get_user_model()


def set_chromedriver_options(more_options=[]):
    """Set the necessary options for the Chrome WebDriver to function correctly."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")

    if more_options:
        for option in more_options:
            options.add_argument(option)

    driver = webdriver.Chrome(options=options)

    return driver


class BaseRoomTest(ChannelsLiveServerTestCase):
    """
    Base test class for testing room-related views.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the Selenium WebDriver for use in the test suite.
        """
        super().setUpClass()
        try:
            cls.driver = set_chromedriver_options()
        except:
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        """
        Teardown method to close the Selenium WebDriver after all tests have been run.
        """
        cls.driver.quit()
        super().tearDownClass()

    def _open_new_window(self):
        """
        Open a new browser window in the current WebDriver session.
        """
        self.driver.execute_script('window.open("about:blank", "_blank");')
        self._switch_to_window(-1)

    def _switch_to_window(self, window_index):
        """
        Switch to a specific window in the WebDriver session.
        """
        self.driver.switch_to.window(self.driver.window_handles[window_index])

    def _post_message(self, message: str, driver=None):
        """
        Post a message in the chat room.
        If a driver is passed, use that driver, Otherwise, use the
        default driver defined in the class.
        """
        current_driver = driver or self.driver
        WebDriverWait(current_driver, 10).until(
            EC.presence_of_element_located((By.ID, 'chat-message-input'))
        )

        input_box = current_driver.find_element(By.ID, 'chat-message-input')
        input_box.send_keys(message)
        input_box.send_keys(Keys.ENTER)

        WebDriverWait(current_driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'message'))
        )

    def _close_all_new_windows(self):
        """
        Close all open windows except the main window.
        """
        while len(self.driver.window_handles) > 1:
            self._switch_to_window(-1)
            self.driver.execute_script("window.close();")

        if len(self.driver.window_handles) == 1:
            self._switch_to_window(0)
            self.driver.execute_script(
                "window.close();")

    def xpath_find(self, xpath: str, driver=None):
        """
        Find an element on the page using an XPath query.
        If a driver is passed, use that driver, Otherwise, use the
        default driver defined in the class.

        """
        current_driver = driver or self.driver
        return current_driver.find_element(By.XPATH, xpath)

    def _assert_message_in(self, css_class: str, message: str, driver=None):
        """
        Assert if the message was successfuly sended.
        If a driver is passed, use that driver, Otherwise, use the
        default driver defined in the class.
        """
        current_driver = driver or self.driver
        response = current_driver.find_element(By.CLASS_NAME, css_class)
        response = response.text.split()
        self.assertEqual(response[0], message)


class PublicRoomTest(BaseRoomTest):
    """
    Tests for the public room view.
    """

    def _enter_chat_room(self, room_name, username):
        """
        Enter a chat room by providing the room name and username.
        """
        self.driver.get(self.live_server_url)
        room_input = self.driver.find_element(By.ID, 'room-name-input')
        username_input = self.driver.find_element(By.ID, 'username-input')
        button = self.driver.find_element(By.ID, 'room-name-submit')

        room_input.send_keys(room_name)
        username_input.send_keys(username)
        button.click()

        WebDriverWait(self.driver, 2).until(
            lambda _: room_name in self.driver.current_url
        )

    def test_send_message(self):
        """
        Test sending a message and the other participants of the room could 
        see the message.
        """
        self._enter_chat_room("room_1", 'usertest1')
        self._open_new_window()
        self._enter_chat_room("room_1", 'usertest2')
        self._switch_to_window(0)

        self._post_message("hello")
        self._assert_message_in('my-message', 'hello')

        self._switch_to_window(1)

        other_user_name = self.xpath_find(
            '/html/body/div[2]/div[1]/div/div')

        message2 = self.driver.find_element(By.CLASS_NAME, 'other-message')
        self.assertEqual('usertest1', other_user_name.text)
        self.assertEqual('usertest1\nhello', message2.text)

        self._close_all_new_windows()

    def test_other_rooms_cant_see_message(self):
        """
        Test the other user in other rooms cant see the message.
        """
        self._enter_chat_room("room_1", 'testuser1')
        self._open_new_window()
        self._enter_chat_room("room_2", 'testuser2')
        self._switch_to_window(0)

        self._post_message("hello")
        self._assert_message_in('my-message', 'hello')

        self._switch_to_window(1)
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.CLASS_NAME, 'other-message')

        self._close_all_new_windows()


class PersonalChatTest(BaseRoomTest):
    """
    Tests for personal chat views.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            cls.data_user = {
                'username': 'testuser1',
                'email': 'user1@test.com',
                'password': 'testpassword1'

            }
            cls.user = User.objects.create_user(**cls.data_user)

            cls.data_user2 = {
                'username': 'testuser2',
                'email': 'user2@test.com',
                'password': 'testpassword2'
            }
            cls.user2 = User.objects.create_user(**cls.data_user2)

            more_options = ['--incognito',]

            cls.driver = set_chromedriver_options()
            cls.driver2 = set_chromedriver_options(more_options)
        except:
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def _enter_chat_room(self, driver, user, friend_name):
        """
        Enter a chat room by providing the room name and username.
        """
        driver.get(self.live_server_url + '/login/?')
        username_input = driver.find_element(By.ID, 'id_username')
        password_input = driver.find_element(By.ID, 'id_password')
        button = driver.find_element(By.ID, 'login-button')

        username_input.send_keys(user['username'])
        password_input.send_keys(user['password'])
        button.click()

        friend = driver.find_element(By.ID, 'personal-chat-friend')
        button = driver.find_element(By.ID, 'personal-chat-submit')

        friend.send_keys(friend_name)
        button.click()

        WebDriverWait(driver, 2).until(
            lambda _: driver.title == f'{friend_name} Chat'
        )

    def test_sending_messages(self):
        self._enter_chat_room(
            self.driver, self.data_user, self.user2.username
        )
        self._enter_chat_room(
            self.driver2, self.data_user2, self.user.username
        )

        self._post_message('hello')
        self._assert_message_in('my-message', 'hello')

        self._post_message('test', self.driver2)
        self._assert_message_in('my-message', 'test', self.driver2)

        self._assert_message_in('other-message', 'test')
