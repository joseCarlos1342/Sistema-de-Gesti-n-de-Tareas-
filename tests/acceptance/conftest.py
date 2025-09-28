import pytest
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for acceptance tests."""
    app = create_app(testing=True)
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5555'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

        # Create test users
        admin_user = User(
            name='Admin Test',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        regular_user = User(
            name='User Test',
            email='user@test.com',
            password_hash=generate_password_hash('user123'),
            role='user'
        )

        db.session.add_all([admin_user, regular_user])
        db.session.commit()

        yield app

        db.drop_all()

@pytest.fixture(scope="session")
def live_server(app):
    """Start a live server for acceptance tests."""
    import socket
    from contextlib import closing

    def find_free_port():
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    port = find_free_port()

    server_thread = threading.Thread(
        target=lambda: app.run(host='localhost', port=port, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to start
    time.sleep(3)

    class LiveServer:
        def __init__(self, app, url):
            self.app = app
            self.url = url

    yield LiveServer(app, f'http://localhost:{port}')

@pytest.fixture
def driver():
    """Setup Chrome WebDriver for tests."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()

@pytest.fixture
def wait(driver):
    """WebDriver wait instance."""
    return WebDriverWait(driver, 10)

class BasePage:
    """Base page class with common functionality."""

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def get(self, path=""):
        """Navigate to a path."""
        base = self.base_url.url if hasattr(self.base_url, 'url') else self.base_url
        self.driver.get(f"{base}{path}")

    def find_element(self, by, value):
        """Find element with wait."""
        wait = WebDriverWait(self.driver, 10)
        return wait.until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by, value):
        """Find multiple elements."""
        return self.driver.find_elements(by, value)

    def click_element(self, by, value):
        """Click element with wait."""
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.click()

    def fill_input(self, by, value, text):
        """Fill input field."""
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)

    def wait_for_text(self, text, timeout=10):
        """Wait for text to appear on page."""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text))

class LoginPage(BasePage):
    """Login page object."""

    def login(self, email, password):
        """Perform login."""
        self.get("/auth/login")

        self.fill_input(By.NAME, "email", email)
        self.fill_input(By.NAME, "password", password)
        self.click_element(By.CSS_SELECTOR, "button[type='submit']")

class RegisterPage(BasePage):
    """Register page object."""

    def register(self, name, email, password):
        """Perform registration."""
        self.get("/auth/register")

        self.fill_input(By.NAME, "name", name)
        self.fill_input(By.NAME, "email", email)
        self.fill_input(By.NAME, "password", password)
        self.fill_input(By.NAME, "password_confirm", password)
        self.click_element(By.CSS_SELECTOR, "button[type='submit']")

class TaskPage(BasePage):
    """Task page object."""

    def create_task(self, title, description="", priority="medium", due_date=""):
        """Create a new task."""
        self.get("/tasks/new")

        self.fill_input(By.NAME, "title", title)
        if description:
            self.fill_input(By.NAME, "description", description)

        # Select priority
        priority_select = self.find_element(By.NAME, "priority")
        for option in priority_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == priority:
                option.click()
                break

        if due_date:
            self.fill_input(By.NAME, "due_date", due_date)

        self.click_element(By.CSS_SELECTOR, "button[type='submit']")

    def search_tasks(self, search_term):
        """Search for tasks."""
        self.get("/tasks/")
        self.fill_input(By.NAME, "search", search_term)
        self.click_element(By.CSS_SELECTOR, "button[type='submit']")

    def filter_by_status(self, status):
        """Filter tasks by status."""
        self.get("/tasks/")
        status_select = self.find_element(By.NAME, "status")
        for option in status_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == status:
                option.click()
                break
        self.click_element(By.CSS_SELECTOR, "button[type='submit']")

@pytest.fixture
def login_page(driver, live_server):
    """Login page object fixture."""
    return LoginPage(driver, live_server)

@pytest.fixture
def register_page(driver, live_server):
    """Register page object fixture."""
    return RegisterPage(driver, live_server)

@pytest.fixture
def task_page(driver, live_server):
    """Task page object fixture."""
    return TaskPage(driver, live_server)

@pytest.fixture
def logged_in_user(driver, login_page):
    """Fixture for logged in regular user."""
    login_page.login("user@test.com", "user123")
    return driver

@pytest.fixture
def logged_in_admin(driver, login_page):
    """Fixture for logged in admin user."""
    login_page.login("admin@test.com", "admin123")
    return driver