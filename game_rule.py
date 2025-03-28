import json
import random
from utils import load_json

# def load_json(file_path):
#     """加载JSON文件"""
#     with open(file_path, 'r', encoding='utf-8') as file:
#         return json.load(file)

def random_pick_one_from(player_list):
    """随机从玩家列表中挑选一个选手"""
    return random.choice(player_list)

def compare_team(player1, player2):
    """对比 team 是否一致，处理特殊情况"""
    # 如果选手已退休，team = 'Retired'
    if player1['isRetired']:
        player1_team = 'Retired'
    elif player1['team']['data'] is None:
        player1_team = 'Free Agent'
    else:
        player1_team = player1['team']['data']['name']

    if player2['isRetired']:
        player2_team = 'Retired'
    elif player2['team']['data'] is None:
        player2_team = 'Free Agent'
    else:
        player2_team = player2['team']['data']['name']
    
    if player1_team == player2_team:
        return player2_team
    else:
        return f'Not {player2_team}'

def compare_role(player1, player2):
    role1 = player1['role']['value']
    role2 = player2['role']['value']
    if role1 == role2:
        return f'{role2}'
    else:
        return f'Not {role2}'
    
def compare_nationality(player1, player2, region_data):
    """对比 nationality 是否一致，若不一致则查找赛区"""
    country1 = player1['nationality']['value']
    country2 = player2['nationality']['value']
    
    # 如果国家一致
    if country1 == country2:
        return f"{country2}"
    
    # 查找赛区
    region1 = region_data['countries'].get(country1, {}).get('region')
    region2 = region_data['countries'].get(country2, {}).get('region')
    country_name = region_data['countries'].get(country2, {}).get('name')
    if region1 == region2:
        return f"Same Region but Not {country_name}"
    return f"Not Same Region"

def compare_age(player1, player2):
    """对比年龄差异"""
    age1 = player1['age']['value']
    age2 = player2['age']['value']

    if age1 < age2 - 3:
        return f"{age2}--"
    elif age1 <= age2 + 3 and age1 >= age2 - 3:
        if age1 == age2:
            return f"{age2}"
        return f"{age2}-"
    elif age1 > age2 + 3:
        return f"{age2}++"
    else:
        return f"{age2}+"


def compare_major_appearances(player1, player2):
    """对比 majorAppearances 差异"""
    ma1 = player1['majorAppearances']['value']
    ma2 = player2['majorAppearances']['value']

    if ma1 < ma2 - 1:
        return f"{ma2}--"
    elif ma1 <= ma2 + 1 and ma1 >= ma2 - 1:
        if ma1 == ma2:
            return f"{ma2}"
        return f"{ma2}-"
    elif ma1 > ma2 + 1:
        return f"{ma2}++"
    else:
        return f"{ma2}+"


def main():
    region_data = load_json("./region.json")
    player_list = load_json("./processed_pro_info.json")

    mystery_player = random_pick_one_from(player_list)

    while True:
        user_nickname = input("请输入选手的nickname: ")

        pick_player = None
        for player in player_list:
            if player['nickname'] == user_nickname:
                pick_player = player
                break

        if not pick_player:
            print("未找到该选手的信息！请重新输入！")
            continue
        team_match = compare_team(mystery_player, pick_player)
        nationality_msg = compare_nationality(mystery_player, pick_player, region_data)
        age_msg = compare_age(mystery_player, pick_player)
        ma_msg = compare_major_appearances(mystery_player, pick_player)
        print(f"{team_match}\t{nationality_msg}\t{age_msg}\t{ma_msg}")
        if pick_player['nickname'] == mystery_player['nickname']:
            print("恭喜你猜对了！")
            break
        else:
            print("没有猜中，请继续尝试！\n")

if __name__ == "__main__":
    main()