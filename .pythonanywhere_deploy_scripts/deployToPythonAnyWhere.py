from time import sleep
import requests, json
from selenium import webdriver
from pyvirtualdisplay import Display

PYTHONANYWHERE_ADDRESS = "https://www.pythonanywhere.com"
API_ADDRESS = f"{PYTHONANYWHERE_ADDRESS}/api/v0/user"

PYTHONANYWHERE_USERNAME = '{{PYTHONANYWHERE_USERNAME}}'
PYTHONANYWHERE_PASSWORD = '{{PYTHONANYWHERE_PASSWORD}}'

TOKEN = '{{BOT_TOKEN}}'
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

print(created_console)

display = Display(visible=0, size=(800, 600))
display.start()

driver = webdriver.Chrome()

driver.get(f'{PYTHONANYWHERE_ADDRESS}{created_console["console_url"]}')
sleep(2)

username_input = driver.find_element_by_name("auth-username")
username_input.send_keys(PYTHONANYWHERE_USERNAME)

password_input = driver.find_element_by_name("auth-password")
password_input.send_keys(PYTHONANYWHERE_PASSWORD)

login_button = driver.find_element_by_id("id_next")
login_button.click()

sleep(4)

print(driver.title)
driver.quit()

display.stop()