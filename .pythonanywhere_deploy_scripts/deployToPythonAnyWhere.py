from time import sleep
import requests, json
from selenium import webdriver
from pyvirtualdisplay import Display

PYTHONANYWHERE_ADDRESS = "https://www.pythonanywhere.com"
API_ADDRESS = f"{PYTHONANYWHERE_ADDRESS}/api/v0/user"

PYTHONANYWHERE_USERNAME = '{{PYTHONANYWHERE_USERNAME}}'
PYTHONANYWHERE_PASSWORD = '{{PYTHONANYWHERE_PASSWORD}}'

TOKEN = '{{PYTHONANYWHERE_TOKEN}}'
FILE_NAME = 'RadioSemicolonBot.py'


def Get(api):
    response = requests.get(
        f'{API_ADDRESS}/{PYTHONANYWHERE_USERNAME}/{api}/',
        headers={'Authorization': f'Token {TOKEN}'}
    ) 
        
    return json.loads(response.content)

def Post(api, data = None, files = None):
    if not data:
        data = {}

    if files :
        response = requests.post(
            f'{API_ADDRESS}/{PYTHONANYWHERE_USERNAME}/{api}/',
            files=files,
            headers={'Authorization': f'Token {TOKEN}'}
        )
    else:
        response = requests.post(
        f'{API_ADDRESS}/{PYTHONANYWHERE_USERNAME}/{api}/',
        data=data,
        headers={'Authorization': f'Token {TOKEN}'}
        )

    if response.content:
        return json.loads(response.content)
    return response.content

def Delete(api):
    requests.delete(
        f'{API_ADDRESS}/{PYTHONANYWHERE_USERNAME}/{api}/',
        headers={'Authorization': f'Token {TOKEN}'}
    )


                        ###################
########################  Delete old file  #########################
                        ###################

Delete(f'files/path/home/{PYTHONANYWHERE_USERNAME}/{FILE_NAME}')



                        ###################
########################  Create new file  #########################
                        ###################

file_content = ''

with open(f'{FILE_NAME}', 'r') as reader:
    file_content = reader.read()

Post(f'files/path/home/{PYTHONANYWHERE_USERNAME}/{FILE_NAME}', files = {'content': file_content})


                        ####################
######################## Delete old console #########################
                        ####################

consoles = Get('consoles')

if len(consoles) > 0:
    Delete(f'consoles/{consoles[-1]["id"]}')


                        ####################
######################## Create new console #########################
                        ####################

created_console = Post('consoles', {'executable': 'python3.6', 'arguments': f'{FILE_NAME}', 'working_directory': None})


                      #########################
###################### Starting the new console ######################
                      #########################

# In order to the new created console starts to work, it must be opened
# throw a browser so in the block of code we will open a selenium browser
# navigate to url of console

# Creating a virtual display which selenium's browser will use
display = Display(visible=0, size=(800, 600))
display.start()

# Creating the selenium browser and navigate to console's url
driver = webdriver.Chrome()
driver.get(f'{PYTHONANYWHERE_ADDRESS}{created_console["console_url"]}')
sleep(2)

# Providing the credentials on login page and loging-in
username_input = driver.find_element_by_name("auth-username")
username_input.send_keys(PYTHONANYWHERE_USERNAME)

password_input = driver.find_element_by_name("auth-password")
password_input.send_keys(PYTHONANYWHERE_PASSWORD)

login_button = driver.find_element_by_id("id_next")
login_button.click()
sleep(4)

# Quite the selenium browser and stop the virtual display
driver.quit()
display.stop()