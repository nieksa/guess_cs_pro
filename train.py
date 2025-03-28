# game_environment.py
import gym
import numpy as np
from gym import spaces
from collections import deque
from game_rule import compare_age,compare_major_appearances,compare_nationality,compare_role,compare_team

class GuessThePlayerEnv(gym.Env):
    def __init__(self, players, regions, max_guesses=8):
        self.players = players  # 275个选手的list
        self.action_space = spaces.Discrete(275)  # 关键设置：动作空间0-274
        self.region_data = regions
        self.max_guesses = max_guesses
        self.obs_features = 8  # 当前特征维度
        self.observation_space = spaces.Box(
            low=-1, high=1,
            shape=(self.obs_features * max_guesses,),  # 8次猜测历史×8特征
            dtype=np.float32
        )
        self.history = deque(maxlen=max_guesses)
        self.remaining_guesses = max_guesses
        self.reset()

    def reset(self):
        """重置环境，随机选择新目标"""
        self.history.clear()
        self.remaining_guesses = self.max_guesses
        self.target_idx = np.random.randint(0, 275)
        self.target = self.players[self.target_idx]
        # 用空特征初始化历史
        for _ in range(self.max_guesses):
            self.history.append(np.zeros(self.obs_features, dtype=np.float32))
        
        return self._get_obs()

    def _encode_feedback(self, guessed_player):
        """核心编码逻辑（当前猜测的特征提取）"""
        target = self.target
        
        # 特征1: 战队匹配（二元）
        team_match = -1.0 if 'Not' in compare_team(guessed_player, target) else 1.0
        
        # 特征2: 角色匹配（二元）
        role_match = -1.0 if 'Not' in compare_role(guessed_player, target) else 1.0
        
        # 特征3: 赛区/国籍（三分类编码）
        nation_result = compare_nationality(guessed_player, target, self.region_data)
        if "Not Same Region" in nation_result:
            nation_code = -1.0
        elif "Same Region but Not" in nation_result:
            nation_code = 0.0
        else:
            nation_code = 1.0
        
        # 特征4: 年龄差异（连续编码）
        age_diff = self._parse_comparison(
            compare_age(guessed_player, target),
            suffixes=['--', '-', '', '+', '++'],
            values=[-1.0, -0.5, 0.0, 0.5, 1.0]
        )
        
        # 特征5: Major参赛次数（连续编码）
        major_diff = self._parse_comparison(
            compare_major_appearances(guessed_player, target),
            suffixes=['--', '-', '', '+', '++'],
            values=[-1.0, -0.5, 0.0, 0.5, 1.0]
        )
        
        return np.array([
            team_match,
            role_match,
            nation_code,
            age_diff,
            major_diff,
            team_match * nation_code,    # 战队与国籍关联
            role_match * major_diff,     # 角色与Major关联
            age_diff * major_diff        # 年龄与Major经验关联
        ], dtype=np.float32)
    
    def _parse_comparison(self, result, suffixes, values):
        """通用解析比较结果的工具函数"""
        for suffix, value in zip(suffixes, values):
            if result.endswith(suffix):
                return value
        return 0.0  # 默认值
    
    def _get_obs(self):
        """构建包含历史信息的观察向量"""
        return np.concatenate(self.history, axis=0)
    
    def step(self, action_idx):
        """执行猜测动作"""
        assert self.action_space.contains(action_idx), f"非法动作：{action_idx}"
        self.remaining_guesses -= 1
        guessed_player = self.players[action_idx]
        current_features = self._encode_feedback(guessed_player)
        
        # 更新历史记录（先入先出）
        self.history.append(current_features)
        
        # 计算奖励（新增渐进奖励机制）
        if action_idx == self.target_idx:
            reward = 100 + 10*(self.max_guesses - len(self.history))  # 越早猜中奖励越高
            done = True
        else:
            # 基于特征相似度的渐进奖励
            similarity = np.dot(current_features, self._encode_feedback(self.target))
            reward = similarity - 0.5  # 范围[-1.5, 0.5]
            done = False
        
        # 终止条件
        done = (self.remaining_guesses <= 0) or (action_idx == self.target_idx)
        return self._get_obs(), reward, done, {}

# 使用示例
if __name__ == "__main__":
    from config import Config
    from utils import load_json
    
    players = load_json(Config.PLAYER_DATA_PATH)
    regions = load_json(Config.REGION_DATA_PATH)
    
    env = GuessThePlayerEnv(players, regions, max_guesses=275)
    # 修改后的测试代码（包含调试信息）
    obs = env.reset()
    target_nickname = env.target['nickname']
    print(f"=== 新游戏开始 ===")
    print(f"待猜选手昵称: {target_nickname}")
    print(f"目标索引（开发者调试用）: {env.target_idx}")

    for step in range(1, env.max_guesses+1):
        # 测试策略：前7次随机猜测，最后一次强制正确
        if step < env.max_guesses:
            action = env.action_space.sample()
        else:
            # action = env.target_idx  # 最后一次强制正确
            action = env.action_space.sample()
        
        obs, reward, done, _ = env.step(action)
        
        print(f"\n第 {step} 次猜测:")
        print(f"选择选手: {env.players[action]['nickname']}")
        print(f"奖励值: {reward:.2f}")
        
        if done:
            if action == env.target_idx:
                print(f"成功猜中目标！选手昵称: {target_nickname}")
            else:
                print("次数用尽，游戏失败")
            break