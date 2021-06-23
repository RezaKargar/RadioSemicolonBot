import requests, json, time, os

BASE_URL = 'https://api.telegram.org/bot'
TOKEN = os.environ['RADIO_SEMICOLON_BOT_TOKEN']
LOG_DIRECTORY =  os.getcwd() + '/logs'

last_update_id = 0
time_stamps_of_removed_users_log_files = [int(time.time())]
time_stamps_of_errors_log_files = [int(time.time())]

def log(text, isError = False):
    global time_stamps_of_removed_users_log_files
    
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

            if 'new_chat_member' in message or 'left_chat_member' in message:
                api('deleteMessage', {
                    'chat_id': chat_id,
                    'message_id': message['message_id']
                })

            if 'new_chat_member' in message:
                new_chat_member_info = api('getChat', {
                    'chat_id': message['new_chat_member']['id']
                })['result']
                
                username = new_chat_member_info['username']
                user_id = new_chat_member_info['id']
                
                
                if 'bot' in username.lower():
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
        print("Exception:")
        print(str(e))
        log(str(e), True)
        time.sleep(10)
