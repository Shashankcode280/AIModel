import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import mtranslate as mt

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Get the input language setting from the environment variables.
InputLanguage = env_vars.get("InputLanguage", "en")  # Default to English if not set
print(f"Loaded input language: {InputLanguage}")  # Debugging

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                if (recognition) recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
                recognition = null;
            }
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language.
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Ensure "Data" folder exists
os.makedirs("Data", exist_ok=True)

# Write the modified HTML code to a file.
html_file_path = os.path.join("Data", "Voice.html")
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Get the absolute file path and format it properly for Windows
current_dir = os.getcwd()
Link = f"file:///{current_dir.replace(os.sep, '/')}/Data/Voice.html"

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# Removing headless mode since speech recognition needs UI interaction
# chrome_options.add_argument("--headless")

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)  # Ensure directory exists

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "was"]

    # Check if the query is a question and add a question mark if necessary.
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speech recognition using the WebDriver.
def SpeechRecognition():
    # Open the HTML file in the browser.
    driver.get(Link)

    # Start speech recognition by clicking the start button.
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            # Get the recognized text from the HTML output element.
            Text = driver.find_element(By.ID, "output").text

            if Text:
                # Stop recognition by clicking the stop button.
                driver.find_element(By.ID, "end").click()

                # If the input language is English, return the modified query.
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    # If the input language is not English, translate the text and return it.
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            print(f"Error in SpeechRecognition: {e}")  # Debugging

# Main execution block.
if __name__ == "__main__":
    while True:
        # Continuously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        if Text:
            print(Text)
