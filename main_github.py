import requests
import json
import vk_api

if __name__ == "__main__":
    # ПЕРВАЯ ЧАСТЬ

    access_token = 'ДЛЯ_БЕЗОПАСНОСТИ_НЕ_ВЫКЛАДЫВАЮ_В_ОТКРЫТЫЙ_ДОСТУП'
    user_name = 'mikle-viter'
    base_url = 'https://api.github.com/users/' + user_name + '/repos'
    params = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer <' + access_token + '>',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    req = requests.get(base_url, params=params)

    file = open('repos.json', 'w')
    file.write(json.dumps(req.json()))
    file.close()

    file = open('repos.json', 'r')
    print(file.read())
    file.close()

    # ВТОРАЯ ЧАСТЬ
    user_id = '124453051'
    access_token = "ДЛЯ_БЕЗОПАСНОСТИ_НЕ_ВЫКЛАДЫВАЮ_В_ОТКРЫТЫЙ_ДОСТУП"

    vk_session = vk_api.VkApi(token=access_token)

    response = vk_session.method("groups.get", {"user_id": user_id, "extended": False, "count": 1000})

    user_groups = response["items"]

    # Выводим названия сообществ
    file = open('user_groups.txt', 'w')
    i = 1
    for group in user_groups:
        print(i.__str__() + ") " + group["name"])
        file.write(i.__str__() + ") " + group["name"]+'\n')
        i += 1
    file.close()