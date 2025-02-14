import pytest
import time
import os
import subprocess
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

pytestmark = pytest.mark.django_db(transaction=True)

class ScreenRecorder:
    def __init__(self, output_dir="../recordings"):
        self.output_dir = os.path.abspath(output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.process = None
        print(f"\nScreen recorder initialized. Output directory: {self.output_dir}")
        
    def start(self, driver):
        """Start recording the screen using ffmpeg.
        Args:
            driver: Selenium WebDriver instance to get window position and size
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"demo_{timestamp}.mp4")
            
            # Get window position and size
            window_size = driver.get_window_size()
            window_pos = driver.get_window_position()
            
            # Add small margin to ensure we capture the full window
            margin = 2
            x = max(0, window_pos['x'] - margin)
            y = max(0, window_pos['y'] - margin)
            width = window_size['width'] + (2 * margin)
            height = window_size['height'] + (2 * margin)
            
            # FFmpeg command to record screen
            command = [
                'ffmpeg',
                '-f', 'x11grab',  # X11 display grabber
                '-video_size', f'{width}x{height}',  # window size
                '-framerate', '30',
                '-i', f':0.0+{x},{y}',  # capture offset
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-y',  # overwrite output file if exists
                output_file
            ]
            
            print(f"\nStarting screen recording...")
            print(f"Capturing window: {width}x{height} at position ({x},{y})")
            print(f"Command: {' '.join(command)}")
            print(f"Output file: {output_file}")
            
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.output_file = output_file
            
            # Check if process started successfully
            time.sleep(1)
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                print("\nFFmpeg failed to start!")
                print(f"Exit code: {self.process.returncode}")
                print(f"stdout: {stdout.decode()}")
                print(f"stderr: {stderr.decode()}")
                raise Exception("FFmpeg failed to start")
                
            print(f"Recording started successfully")
            time.sleep(2)  # Give ffmpeg time to start
            
        except Exception as e:
            print(f"\nError starting screen recording: {str(e)}")
            if self.process:
                self.process.terminate()
            raise
        
    def stop(self):
        """Stop the recording process."""
        if self.process:
            try:
                print("\nStopping screen recording...")
                self.process.terminate()
                stdout, stderr = self.process.communicate()
                print(f"FFmpeg output: {stderr.decode()}")
                if os.path.exists(self.output_file):
                    size = os.path.getsize(self.output_file)
                    print(f"Recording saved to: {self.output_file} (size: {size/1024/1024:.1f} MB)")
                else:
                    print(f"Warning: Output file not found: {self.output_file}")
            except Exception as e:
                print(f"Error stopping screen recording: {str(e)}")

def demo_delay(duration=1):
    """Add a delay to make the demo easy to follow.
    Args:
        duration (int): Number of seconds to delay. Default is 1 second.
    """
    time.sleep(duration)

def move_cursor_to(driver, element, click=False, type_text=False):
    """Move a simulated cursor to the element's position.
    Args:
        driver: Selenium WebDriver instance
        element: WebElement to move cursor to
        click: Whether to show click animation
        type_text: Whether to show typing indicator
    """
    # Create cursor if it doesn't exist
    driver.execute_script("""
        if (!document.getElementById('demo-cursor')) {
            const cursor = document.createElement('div');
            cursor.id = 'demo-cursor';
            cursor.style.position = 'fixed';
            cursor.style.width = '20px';
            cursor.style.height = '20px';
            cursor.style.backgroundColor = '#ff4444';
            cursor.style.borderRadius = '50%';
            cursor.style.pointerEvents = 'none';
            cursor.style.transition = 'all 0.5s ease';
            cursor.style.zIndex = '10000';
            cursor.style.opacity = '0.5';
            cursor.style.boxShadow = '0 0 10px rgba(255,68,68,0.5)';
            document.body.appendChild(cursor);
        }
        
        // Add keyframes for click animation if they don't exist
        if (!document.getElementById('cursor-animations')) {
            const style = document.createElement('style');
            style.id = 'cursor-animations';
            style.textContent = `
                @keyframes cursorClick {
                    0% { transform: scale(1); }
                    50% { transform: scale(0.8); }
                    100% { transform: scale(1); }
                }
                @keyframes cursorType {
                    0% { opacity: 0.5; }
                    50% { opacity: 1; }
                    100% { opacity: 0.5; }
                }
            `;
            document.head.appendChild(style);
        }
    """)
    
    # Move cursor to element with animation
    driver.execute_script("""
        const cursor = document.getElementById('demo-cursor');
        const rect = arguments[0].getBoundingClientRect();
        const x = rect.left + (rect.width / 2);
        const y = rect.top + (rect.height / 2);
        cursor.style.left = x + 'px';
        cursor.style.top = y + 'px';
    """, element)
    time.sleep(0.5)  # Wait for movement animation
    
    if click:
        # Show click animation
        driver.execute_script("""
            const cursor = document.getElementById('demo-cursor');
            cursor.style.animation = 'cursorClick 0.3s ease';
            setTimeout(() => {
                cursor.style.animation = '';
            }, 300);
        """)
        time.sleep(0.3)  # Wait for click animation
    
    if type_text:
        # Show typing indicator
        driver.execute_script("""
            const cursor = document.getElementById('demo-cursor');
            cursor.style.animation = 'cursorType 1s ease infinite';
        """)

@pytest.fixture(scope='session')
def selenium_fixture():
    """Create a new selenium driver for the demo."""
    options = Options()
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope='session')
def screen_recorder():
    """Fixture to handle screen recording."""
    recorder = ScreenRecorder()
    yield recorder
    recorder.stop()

def test_student_journey_happy_case(selenium_fixture, live_server, caplog, hash_user_passwords, screen_recorder):
    """Demonstrate a typical student journey through the platform."""
    # Set up browser window - position it on the secondary monitor (DP-1)
    selenium_fixture.set_window_position(0, 0)  # Secondary monitor starts at x=0
    selenium_fixture.set_window_size(1600, 1000)  # Taller window but not too tall
    
    # Start recording
    screen_recorder.start(selenium_fixture)
    
    # Open the home page
    selenium_fixture.get(live_server.url)
    
    # Give time to start recording
    time.sleep(5)  # First delay to start recording
    time.sleep(5)  # Second delay to get ready
    
    # Continue with the demo
    demo_delay(2)  # Initial page load

    # Click login link
    login_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='nav-link' and text()='Login']"))
        )
    move_cursor_to(selenium_fixture, login_link, click=True)
    login_link.click()
    demo_delay(2)  # After clicking login

    # Find username and password fields and submit button
    username_input = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_input = selenium_fixture.find_element(By.NAME, "password")
    submit_button = selenium_fixture.find_element(By.XPATH, "//button[@type='submit']")

    # Fill in the form with test student credentials from fixture
    move_cursor_to(selenium_fixture, username_input, click=True, type_text=True)
    username_input.send_keys('alice')
    demo_delay(1)
    move_cursor_to(selenium_fixture, password_input, click=True, type_text=True)
    password_input.send_keys('student123')
    demo_delay(3)  # Show filled login form

    # Submit the form
    move_cursor_to(selenium_fixture, submit_button, click=True)
    submit_button.click()
    demo_delay(2)  # After login submission

    # After successful login, we should see the logout link
    logout_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='nav-link' and text()='Logout']"))
    )
    assert logout_link.is_displayed()
    demo_delay(2)  # Show logged in state
    
    # The login link should no longer be visible
    login_links = selenium_fixture.find_elements(By.XPATH, "//a[@class='nav-link' and text()='Login']")
    assert len(login_links) == 0
    
    # Go to course list
    selenium_fixture.get(f"{live_server.url}/courses/")
    demo_delay(3)  # Show course list
    
    # For enrolled course, should see "Continue Learning"
    enrolled_course_button = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'course-card') and contains(., 'Python for Beginners')]//a[text()='Continue Learning']"))
    )
    assert enrolled_course_button.is_displayed()
    
    # For non-enrolled course, should see "Enroll"
    non_enrolled_button = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'course-card') and contains(., 'Advanced Django')]//a[text()='Enroll']"))
    )
    assert non_enrolled_button.is_displayed()

    # Click Continue Learning to view course units
    enrolled_course_button.click()
    demo_delay(3)  # Show unit list

    # Click on the first unit
    unit_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'unit-card')]//a[contains(., 'Installing Python')]"))
    )
    move_cursor_to(selenium_fixture, unit_link)
    unit_link.click()
    demo_delay(3)  # Show unit details

    # Check unit details page
    unit_title = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Installing Python')]"))
    )
    assert unit_title.is_displayed()

    # Check for resources section
    resources_heading = selenium_fixture.find_element(By.XPATH, "//h2[text()='Resources']")
    assert resources_heading.is_displayed()

    # Check that resources are listed
    resources_list = selenium_fixture.find_element(By.XPATH, "//div[@id='resources-list']")
    assert resources_list.is_displayed()

    # Debug: print resources list HTML
    print("\nResources list HTML:")
    print(resources_list.get_attribute('innerHTML'))
    print()

    # Visit Installation Guide
    guide_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h5[contains(@class, 'text-primary') and contains(text(), 'Python Installation Guide')]"))
    )
    move_cursor_to(selenium_fixture, guide_link)
    guide_link.click()
    demo_delay(3)  # Show resource page

    # Verify markdown content is displayed
    markdown_content = selenium_fixture.find_element(By.XPATH, "//div[contains(@class, 'markdown-content')]")
    assert markdown_content.is_displayed()
    demo_delay(2)  # Show markdown content
    
    # Mark guide as completed
    complete_button = WebDriverWait(selenium_fixture, 10).until(
        EC.element_to_be_clickable((By.ID, "mark-completed"))
    )
    move_cursor_to(selenium_fixture, complete_button)
    selenium_fixture.execute_script("arguments[0].scrollIntoView();", complete_button)
    selenium_fixture.execute_script("arguments[0].click();", complete_button)
    demo_delay(2)  # Show completion status

    # Visit Verifying Your Installation
    verify_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[self::h5 or self::h6][contains(@class, 'mb-1') and contains(text(), 'Verifying Your Installation')]"))
    )
    # Get the parent link element
    verify_link = verify_link.find_element(By.XPATH, "./..")  # Get div
    verify_link = verify_link.find_element(By.XPATH, "./..")  # Get parent link
    move_cursor_to(selenium_fixture, verify_link)
    verify_link.click()
    demo_delay(3)  # Show resource page

    # Verify markdown content is displayed
    markdown_content = selenium_fixture.find_element(By.XPATH, "//div[contains(@class, 'markdown-content')]")
    assert markdown_content.is_displayed()
    demo_delay(2)  # Show markdown content
    
    # Mark as completed
    complete_button = WebDriverWait(selenium_fixture, 10).until(
        EC.element_to_be_clickable((By.ID, "mark-completed"))
    )
    move_cursor_to(selenium_fixture, complete_button)
    selenium_fixture.execute_script("arguments[0].scrollIntoView();", complete_button)
    selenium_fixture.execute_script("arguments[0].click();", complete_button)
    demo_delay(2)  # Show completion status

    # Visit Video
    video_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[self::h5 or self::h6][contains(@class, 'mb-1') and contains(text(), 'Raspberry Pi Pico Oscilloscope')]"))
    )
    # Get the parent link element
    video_link = video_link.find_element(By.XPATH, "./..")  # Get div
    video_link = video_link.find_element(By.XPATH, "./..")  # Get parent link
    move_cursor_to(selenium_fixture, video_link)
    video_link.click()
    demo_delay(3)  # Show video page
        
    # Wait for video player to load
    video_player = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    assert video_player.is_displayed()
    demo_delay(2)  # Show video player

    # Switch to iframe and try to play video
    selenium_fixture.switch_to.frame(video_player)
    try:
        # Wait for the YouTube player to load
        play_button = WebDriverWait(selenium_fixture, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ytp-large-play-button"))
        )
        # Click play button
        move_cursor_to(selenium_fixture, play_button)
        play_button.click()
        demo_delay(5)  # Watch video briefly

        # Click pause button (same element after playing)
        pause_button = selenium_fixture.find_element(By.CLASS_NAME, "ytp-play-button")
        move_cursor_to(selenium_fixture, pause_button)
        pause_button.click()
    except:
        print("Could not interact with video player, continuing with demo")
    finally:
        # Switch back to default content
        selenium_fixture.switch_to.default_content()
    demo_delay(2)  # Show video player

    # Mark video as completed
    complete_button = WebDriverWait(selenium_fixture, 10).until(
        EC.element_to_be_clickable((By.ID, "mark-completed"))
    )
    move_cursor_to(selenium_fixture, complete_button)
    selenium_fixture.execute_script("arguments[0].scrollIntoView();", complete_button)
    selenium_fixture.execute_script("arguments[0].click();", complete_button)
    demo_delay(2)  # Show completion status

    # Visit Quiz
    quiz_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[self::h5 or self::h6][contains(@class, 'mb-1') and contains(text(), 'Python Basics Quiz')]"))
    )
    # Get the parent link element
    quiz_link = quiz_link.find_element(By.XPATH, "./..")  # Get div
    quiz_link = quiz_link.find_element(By.XPATH, "./..")  # Get parent link
    move_cursor_to(selenium_fixture, quiz_link)
    quiz_link.click()
    demo_delay(3)  # Show quiz page

    # Verify we're on the quiz page
    quiz_title = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Python Basics Quiz')]"))
    )
    assert quiz_title.is_displayed()

    # Wait for quiz elements to be present and visible
    WebDriverWait(selenium_fixture, 10).until(
        EC.visibility_of_element_located((By.ID, "question-text"))
    )
    WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#options-container .form-check"))
    )

    # Get all quiz elements
    question_text = selenium_fixture.find_element(By.ID, "question-text")
    options_container = selenium_fixture.find_element(By.ID, "options-container")
    check_answer_button = selenium_fixture.find_element(By.ID, "check-answer")
    show_hint_button = selenium_fixture.find_element(By.ID, "show-hint")
    show_answer_button = selenium_fixture.find_element(By.ID, "show-answer")

    # Debug: print quiz content
    print("\nQuestion text:", question_text.text)
    print("\nOptions container HTML:", options_container.get_attribute('innerHTML'))
            
    assert question_text.is_displayed()
    assert options_container.is_displayed()
    assert check_answer_button.is_displayed()
    assert show_hint_button.is_displayed()
    assert show_answer_button.is_displayed()
    demo_delay(2)  # Show quiz content

    # Wait for options to be loaded
    WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#options-container .form-check"))
    )
            
    options = selenium_fixture.find_elements(By.CSS_SELECTOR, "#options-container input[type='radio']")
    option_labels = selenium_fixture.find_elements(By.CSS_SELECTOR, "#options-container .form-check-label")
                
    # Debug: print all options
    print("\nAvailable options:")
    for i, label in enumerate(option_labels):
        print(f"Option {i}: {label.text}")
    print()

    # Find and click the correct option (first one - "<class 'int'>")
    correct_option_clicked = False
    for i, label in enumerate(option_labels):
        if "<class 'int'>" in label.text:
            print(f"Found correct option at index {i}")
            move_cursor_to(selenium_fixture, options[i])
            options[i].click()
            correct_option_clicked = True
            break
    assert correct_option_clicked, "Could not find the correct option for the first question"
    demo_delay(2)  # Show selected answer

    # Check the answer
    move_cursor_to(selenium_fixture, check_answer_button)
    check_answer_button.click()
    demo_delay(3)  # Show answer feedback

    # Verify feedback is shown and it's correct
    feedback = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )
    assert "Correct" in feedback.text
    demo_delay(2)  # Show correct feedback

    # Move to next question
    next_button = WebDriverWait(selenium_fixture, 10).until(
        EC.element_to_be_clickable((By.ID, "next-question"))
    )
    # Scroll the next button into view and click using JavaScript
    selenium_fixture.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", next_button)
    demo_delay(2)  # Show next question

    # For second question, let's try the hint feature
    show_hint_button = WebDriverWait(selenium_fixture, 10).until(
        EC.element_to_be_clickable((By.ID, "show-hint"))
    )
    move_cursor_to(selenium_fixture, show_hint_button)
    show_hint_button.click()
    demo_delay(3)  # Show hint

    # Verify hint is shown
    hint_container = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-info"))
    )
    assert hint_container.is_displayed()
    demo_delay(2)  # Show hint

    # Wait for options to be loaded for second question
    WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#options-container .form-check"))
    )
            
    # Debug: print all options
    print("\nAvailable options:")
    options = selenium_fixture.find_elements(By.CSS_SELECTOR, "#options-container input[type='radio']")
    option_labels = selenium_fixture.find_elements(By.CSS_SELECTOR, "#options-container .form-check-label")
    for i, label in enumerate(option_labels):
        print(f"Option {i}: {label.text}")
    print()

    # Answer second question (correctly - it's about list creation)
    correct_option_clicked = False
    for i, label in enumerate(option_labels):
        if "[1, 2, 3]" in label.text:
            print(f"Found correct option at index {i}")
            move_cursor_to(selenium_fixture, options[i])
            options[i].click()
            correct_option_clicked = True
            break
    assert correct_option_clicked, "Could not find the correct option for the second question"
    demo_delay(2)  # Show selected answer

    # Check the answer
    check_answer_button = selenium_fixture.find_element(By.ID, "check-answer")
    move_cursor_to(selenium_fixture, check_answer_button)
    check_answer_button.click()
    demo_delay(3)  # Show answer feedback

    # Verify feedback is shown and it's correct
    feedback = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
    )
    assert "Correct" in feedback.text
    demo_delay(2)  # Show correct feedback

    # Mark quiz as completed
    complete_button = WebDriverWait(selenium_fixture, 10).until(
        EC.element_to_be_clickable((By.ID, "mark-completed"))
    )
    move_cursor_to(selenium_fixture, complete_button)
    selenium_fixture.execute_script("arguments[0].scrollIntoView();", complete_button)
    selenium_fixture.execute_script("arguments[0].click();", complete_button)
    demo_delay(2)  # Show completion status

    # Wait for the button to be replaced with completed status
    WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='card-body']//span[contains(@class, 'text-success') and contains(., 'Completed')]"))
    )
    demo_delay(2)  # Show completed status

    # Visit Exercise
    exercise_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[self::h5 or self::h6][contains(@class, 'mb-1') and contains(text(), 'Python Installation Exercise')]"))
    )
    # Get the parent link element
    exercise_link = exercise_link.find_element(By.XPATH, "./..")  # Get div
    exercise_link = exercise_link.find_element(By.XPATH, "./..")  # Get parent link
    move_cursor_to(selenium_fixture, exercise_link)
    exercise_link.click()
    demo_delay(3)  # Show exercise page

    # Answer all questions in the exercise
    questions = selenium_fixture.find_elements(By.CSS_SELECTOR, "#exercise-form .card-body")
    # The correct answers from our fixture are:
    # 1. python --version (index 0)
    # 2. Python's package installer (index 1)
    # 3. Using Microsoft Word (index 3)
    correct_answers = [0, 1, 3]
    for i, question in enumerate(questions):
        radio_button = question.find_element(By.CSS_SELECTOR, f".options input[value='{correct_answers[i]}']")
        # Scroll the radio button into view
        selenium_fixture.execute_script("arguments[0].scrollIntoView();", radio_button)
        demo_delay(1)  # Brief pause before answering
        move_cursor_to(selenium_fixture, radio_button)
        radio_button.click()
        demo_delay(2)  # Show selected answer
    demo_delay(1)  # Brief pause before submitting

    # Submit the exercise
    submit_button = selenium_fixture.find_element(By.XPATH, "//button[text()='Submit Exercise']")
    move_cursor_to(selenium_fixture, submit_button)
    submit_button.click()
    demo_delay(3)  # Show exercise results

    # Wait for completion message
    completion_message = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.ID, "completion-message"))
    )
    assert "Congratulations" in completion_message.text
    demo_delay(3)  # Show completion message

    # Verify score is 100%
    final_score = selenium_fixture.find_element(By.ID, "final-score")
    assert float(final_score.text) == 100.0
    demo_delay(2)  # Show final score

    # Verify progress bar is at 100%
    progress_bar = selenium_fixture.find_element(By.CLASS_NAME, "progress-bar")
    assert progress_bar.get_attribute("style") == "width: 100%;"
    demo_delay(2)  # Show progress bar

    # Mark exercise as completed
    complete_button = WebDriverWait(selenium_fixture, 10).until(
        EC.element_to_be_clickable((By.ID, "mark-completed"))
    )
    move_cursor_to(selenium_fixture, complete_button)
    selenium_fixture.execute_script("arguments[0].scrollIntoView();", complete_button)
    selenium_fixture.execute_script("arguments[0].click();", complete_button)
    demo_delay(2)  # Show completion status

    # Get fresh reference to logout link after completing all resources
    logout_link = WebDriverWait(selenium_fixture, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='nav-link' and text()='Logout']"))
    )
    # Scroll the logout link into view and click it using JavaScript
    selenium_fixture.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", logout_link)
    demo_delay(2)  # Final delay after logout
