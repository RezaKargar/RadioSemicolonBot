import requests, json, time, os, re
from datetime import datetime

BASE_URL = 'https://api.telegram.org/bot'
TOKEN = '{{BOT_TOKEN}}'
LOG_DIRECTORY =  os.getcwd() + '/logs'

BOT_USERNAME = "radiosemicolonbot"

last_update_id = 0
time_stamps_of_removed_users_log_files = [int(time.time())]
time_stamps_of_errors_log_files = [int(time.time())]

def log(text, isError = False):
    global time_stamps_of_removed_users_log_files
    
    time_of_log = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    text = f"{time_of_log} - {text}"

    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)
    
    timestamp = int(time.time())
    tweleve_hour_in_seconds = 12 * 60 * 60

    if not isError:
        if time_stamps_of_removed_users_log_files[-1] + tweleve_hour_in_seconds <= timestamp:
            time_stamps_of_removed_users_log_files.append(timestamp)
            if len(time_stamps_of_removed_users_log_files) > 15:
                remove_old_log_files()

        file_name = f'removed-users-log-{time_stamps_of_removed_users_log_files[-1]}.log'

    else:
        if time_stamps_of_errors_log_files[-1] + tweleve_hour_in_seconds <= timestamp:
            time_stamps_of_errors_log_files.append(timestamp)
        
        file_name = f'errors-log-{time_stamps_of_errors_log_files[-1]}.log'

    with open(f'{LOG_DIRECTORY}/{file_name}', 'a') as writter:
        writter.write(f'{timestamp} - {text}\n')
    
def remove_old_log_files():
    all_files_in_log_directory = next(os.walk(LOG_DIRECTORY), (None, None, []))[2]
    
    removed_users_log_files = [file_name for file_name in all_files_in_log_directory if 'removed-users-log' in file_name]
    removed_users_log_files.sort()
    
    if len(removed_users_log_files) < 15:
        return
    
    removed_users_log_files = removed_users_log_files[:15]

    for file_name in removed_users_log_files[:-15]:
        file_path = f'{LOG_DIRECTORY}/{file_name}'
        if os.path.exists(file_path):
            os.remove(file_path)
    
def api(method, data = None):
    if data is None:
        data = dict()

    response = requests.post(BASE_URL + TOKEN + '/' + method, json=data)
    return json.loads(response.content)

def extract_emojis(text):
    emoji_pattern = re.compile(
        "["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002500-\U00002BEF"
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"
            u"\u3030"
        "]", flags=re.UNICODE)
    return re.findall(emoji_pattern, text)

def extract_diacritical_marks_or_arabic_letters(text):
    diacritical_marks_pattern = re.compile("[أؤكيةًٌٍَّ]")
    return re.findall(diacritical_marks_pattern, text)

def has_whats_up_link(text):
    whats_up_link_pattern = re.compile("(https?://)?wa.me")
    links = re.findall(whats_up_link_pattern, text)
    return len(links) > 0

def is_arabic_spam(text):
    """
        This function is for detecting if a text is an Arabic spam text
        
        The four conditions that make a text Arabic spam:
        1. Having length of more than 1000 characters
        2. Including more than 10 emojis
        3. Including more than 10 diacritical marks or arabic letters
        4. Including a Whats up link

        The condition 2 and 3 are more important
    """
    
    emojis_of_text = extract_emojis(text)
    diacritical_marks_or_arabic_letters = extract_diacritical_marks_or_arabic_letters(text)
    is_any_whats_up_link_in_text = has_whats_up_link(text)

    count_of_conditons_failed = 0

    if len(text) > 1000:
        count_of_conditons_failed += 1

    if len(emojis_of_text) > 10:
        count_of_conditons_failed += 2

    if len(diacritical_marks_or_arabic_letters) > 50:
        count_of_conditons_failed += 2

    if is_any_whats_up_link_in_text:
        count_of_conditons_failed += 1

    return count_of_conditons_failed > 2

remove_old_log_files()

while 1:
    try:
        time.sleep(.5)

        updates = api('getUpdates', {
            'offset': last_update_id + 1,
            'timeout': 40
        })['result']

        print(f'updates count : { len(updates) }')

        if not len(updates):
            continue

        last_update_id = int(updates[-1]['update_id'])

        for update in updates:
            if 'message' not in update:
                continue
            
            message = update['message']
            chat_id = message['chat']['id']

            if 'text' in message:
                if message['text'] == '/ping':
                    api('sendMessage', {
                        'chat_id': chat_id,
                        'reply_to_message_id': message['message_id'],
                        'text': 'Pong',
                    })

                if is_arabic_spam(message['text']):
                    api('deleteMessage', {
                        'chat_id': chat_id,
                        'message_id': message['message_id']
                    })
                    
                    api('kickChatMember', {
                        'chat_id': chat_id,
                        'user_id': user_id,
                        'until_date': 0 #Forever
                    })

                    spammer_first_name = message['chat']['first_name']
                    spammer_last_name = message['chat']['last_name']
                    spammer_user_name = message['chat']['username']
                    
                    print(f'Spammer: @{spammer_user_name} {spammer_first_name} {spammer_last_name}')
                    log(f'Spammer: @{spammer_user_name} {spammer_first_name} {spammer_last_name}')
                    log(f'Spam Text: {message["text"]}')
                    
                    continue

            if 'new_chat_member' in message or 'left_chat_member' in message:
                api('deleteMessage', {
                    'chat_id': chat_id,
                    'message_id': message['message_id']
                })

            if 'new_chat_member' in message:
                new_chat_member_info = api('getChat', {
                    'chat_id': message['new_chat_member']['id']
                })['result']
                
                if 'username' in new_chat_member_info:
                    username = new_chat_member_info['username'].lower()
                    user_id = new_chat_member_info['id']
                    
                    if username == BOT_USERNAME:
                        continue
                    
                    if 'bot' in username:
                        print(f'Bot: @{username}')
                        log(f'Bot: @{username}')
                        
                        api('kickChatMember', {
                            'chat_id': chat_id,
                            'user_id': user_id,
                            'until_date': 0 #Forever
                        })
                        
                        continue
                
                
                if 'bio' not in new_chat_member_info:
                    continue
                
                bio = new_chat_member_info['bio']
                
                has_any_forbidden_words_or_links_in_bio = False
                
                for word in ["https://t.me", "@", "bot", "porn", "sex", "xxx"]:
                    if word in bio:
                        has_any_forbidden_words_or_links_in_bio = True
                        break
                    
                if has_any_forbidden_words_or_links_in_bio:
                    spammer_first_name = message['new_chat_member']['first_name']
                    spammer_last_name = message['new_chat_member']['last_name']
                    spammer_user_name = message['new_chat_member']['user_name']
                    
                    print(f'Spammer: @{spammer_user_name} {spammer_first_name} {spammer_last_name}')
                    log(f'Spammer: @{spammer_user_name} {spammer_first_name} {spammer_last_name}')

                    api('kickChatMember', {
                        'chat_id': chat_id,
                        'user_id': user_id,
                        'until_date': 0 #Forever
                    })

    except Exception as e:
        print(f"Exception: {e}")
        log(str(e), True)
        time.sleep(10)
