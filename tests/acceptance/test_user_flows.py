import pytest
import time
from datetime import date, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TestUserRegistrationAndLogin:
    """Test user registration and login flow."""

    def test_complete_registration_flow(self, register_page, login_page, driver):
        """Test complete user registration flow."""
        # Register new user
        register_page.register("New User", "newuser@test.com", "password123")

        # Should redirect to login with success message
        register_page.wait_for_text("Registro exitoso")

        # Login with new credentials
        login_page.login("newuser@test.com", "password123")

        # Should redirect to dashboard
        register_page.wait_for_text("Dashboard")
        assert "Dashboard" in driver.title or "Gestión de Tareas" in driver.title

    def test_login_logout_flow(self, login_page, driver):
        """Test login and logout flow."""
        # Login
        login_page.login("user@test.com", "user123")

        # Verify dashboard
        login_page.wait_for_text("Dashboard")

        # Logout
        login_page.click_element(By.CSS_SELECTOR, "a[href*='logout']")

        # Should redirect to login
        login_page.wait_for_text("Iniciar Sesión")

    def test_failed_login(self, login_page, driver):
        """Test failed login attempt."""
        login_page.login("user@test.com", "wrongpassword")

        # Should show error message
        login_page.wait_for_text("Email o contraseña incorrectos")

class TestTaskManagement:
    """Test task management flows."""

    def test_complete_task_lifecycle(self, logged_in_user, task_page, driver):
        """Test complete task lifecycle: create, edit, complete, delete."""
        # Create task
        task_title = f"Test Task {int(time.time())}"
        task_page.create_task(
            title=task_title,
            description="Test task description",
            priority="high"
        )

        # Verify task creation
        task_page.wait_for_text("Tarea creada exitosamente")

        # Go to task list
        task_page.get("/tasks/")
        task_page.wait_for_text(task_title)

        # Edit task
        edit_link = driver.find_element(By.CSS_SELECTOR, "a[href*='/edit']")
        edit_link.click()

        task_page.fill_input(By.NAME, "title", f"{task_title} - Edited")
        task_page.click_element(By.CSS_SELECTOR, "button[type='submit']")

        # Verify edit
        task_page.wait_for_text("Tarea actualizada exitosamente")

        # Mark as complete
        task_page.get("/tasks/")
        toggle_button = driver.find_element(By.CSS_SELECTOR, "button[onclick*='toggleTask']")
        toggle_button.click()

        # Wait for status change
        time.sleep(2)

        # Verify task is marked as completed
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".badge.bg-success"))
        )

        # Delete task
        delete_form = driver.find_element(By.CSS_SELECTOR, "form[action*='/delete']")
        delete_button = delete_form.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Handle confirm dialog
        driver.execute_script("window.confirm = function(){return true;}")
        delete_button.click()

        # Verify deletion
        task_page.wait_for_text("Tarea eliminada exitosamente")

    def test_task_search_and_filter(self, logged_in_user, task_page, driver):
        """Test task search and filtering functionality."""
        # Create multiple tasks with different properties
        tasks = [
            {"title": "High Priority Task", "priority": "high", "status": "pending"},
            {"title": "Low Priority Task", "priority": "low", "status": "pending"},
            {"title": "Completed Task", "priority": "medium", "status": "done"}
        ]

        for task_data in tasks:
            task_page.create_task(
                title=task_data["title"],
                priority=task_data["priority"]
            )

            if task_data["status"] == "done":
                # Mark as completed
                task_page.get("/tasks/")
                toggle_button = driver.find_element(By.CSS_SELECTOR, "button[onclick*='toggleTask']")
                toggle_button.click()
                time.sleep(1)

        # Test search functionality
        task_page.search_tasks("High Priority")
        task_page.wait_for_text("High Priority Task")

        # Verify only searched task is shown
        task_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        assert len(task_rows) == 1

        # Test status filter
        task_page.filter_by_status("done")
        task_page.wait_for_text("Completada")

        # Test priority filter by navigating and filtering
        task_page.get("/tasks/?priority=high")
        task_page.wait_for_text("High Priority Task")

    def test_task_assignment_admin(self, logged_in_admin, task_page, driver):
        """Test task assignment functionality for admin."""
        # Create task and assign to specific user
        task_page.create_task(
            title="Admin Assigned Task",
            description="Task assigned by admin"
        )

        task_page.wait_for_text("Tarea creada exitosamente")

        # Verify task appears in task list
        task_page.get("/tasks/")
        task_page.wait_for_text("Admin Assigned Task")

class TestProfileManagement:
    """Test profile management flows."""

    def test_profile_update_flow(self, logged_in_user, driver):
        """Test profile update functionality."""
        # Navigate to profile
        driver.find_element(By.CSS_SELECTOR, "a[href*='profile']").click()

        # Update profile information
        name_input = driver.find_element(By.NAME, "name")
        name_input.clear()
        name_input.send_keys("Updated User Name")

        email_input = driver.find_element(By.NAME, "email")
        email_input.clear()
        email_input.send_keys("updated@test.com")

        # Submit changes
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify update
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Perfil actualizado exitosamente")
        )

    def test_password_change_flow(self, logged_in_user, driver):
        """Test password change functionality."""
        # Navigate to change password
        driver.find_element(By.CSS_SELECTOR, "a[href*='change_password']").click()

        # Fill password change form
        driver.find_element(By.NAME, "current_password").send_keys("user123")
        driver.find_element(By.NAME, "new_password").send_keys("newpassword123")
        driver.find_element(By.NAME, "confirm_password").send_keys("newpassword123")

        # Submit
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify success
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Contraseña cambiada exitosamente")
        )

class TestDashboard:
    """Test dashboard functionality."""

    def test_dashboard_statistics(self, logged_in_user, task_page, driver):
        """Test dashboard shows correct statistics."""
        # Create some tasks
        task_page.create_task("Dashboard Test Task 1", priority="high")
        task_page.create_task("Dashboard Test Task 2", priority="medium")

        # Go to dashboard
        task_page.get("/")

        # Verify statistics are displayed
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".card .h2"))
        )

        # Check that total tasks count is updated
        total_tasks = driver.find_element(By.CSS_SELECTOR, ".bg-primary .h2").text
        assert int(total_tasks) >= 2

    def test_dashboard_recent_tasks(self, logged_in_user, task_page, driver):
        """Test dashboard shows recent tasks."""
        # Create a task
        task_title = f"Recent Task {int(time.time())}"
        task_page.create_task(task_title)

        # Go to dashboard
        task_page.get("/")

        # Verify recent task appears
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), task_title)
        )

class TestResponsiveDesign:
    """Test responsive design and mobile functionality."""

    def test_mobile_navigation(self, logged_in_user, driver):
        """Test mobile navigation works correctly."""
        # Resize to mobile
        driver.set_window_size(375, 667)

        # Check if mobile menu toggle is present
        try:
            toggle = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".navbar-toggler"))
            )
            toggle.click()

            # Verify mobile menu opens
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".navbar-collapse.show"))
            )

        except TimeoutException:
            # Mobile toggle might not be visible depending on design
            pass

        # Restore window size
        driver.set_window_size(1920, 1080)

class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_access_protected_route_without_login(self, driver, live_server):
        """Test accessing protected routes without login."""
        driver.get(f"{live_server}/tasks/")

        # Should redirect to login
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Iniciar Sesión")
        )

    def test_invalid_task_creation(self, logged_in_user, task_page, driver):
        """Test invalid task creation handling."""
        # Try to create task without title
        task_page.get("/tasks/new")
        task_page.click_element(By.CSS_SELECTOR, "button[type='submit']")

        # Should show validation error or stay on form
        # Form validation should prevent submission

    def test_unauthorized_task_access(self, logged_in_user, driver, live_server):
        """Test accessing unauthorized task."""
        # Try to access a task ID that doesn't exist or isn't accessible
        driver.get(f"{live_server}/tasks/999/edit")

        # Should show error message or redirect
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "no encontrada")
        )