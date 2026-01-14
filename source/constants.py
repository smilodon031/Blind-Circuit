SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

# Bot AI configuration per level
# speed: tuned to ensure bot finishes ~10s after player's average time
# reaction_time: how often (in seconds) the bot makes a new decision
# lane_change_chance: probability of switching lanes when stuck behind player
# follow_accuracy: chance to track player's lane vs random wandering
# awareness_distance: pixels ahead the bot can 'see' obstacles
# avoidance_strength: probability to choose a safe lane vs crashing
# panic_chance: probability of making a random move when crashing is imminent
BOT_DIFFICULTY = {
    # Level 1: Player ~50s (208kph) -> Bot ~60s
    1: {"reaction_time": 1.0, "lane_change_chance": 0.05, "follow_accuracy": 0.40, "max_speed": 5.8, "awareness_distance": 200, "avoidance_strength": 0.3, "panic_chance": 0.5},
    # Level 2: Player ~58s (197kph) -> Bot ~68s
    2: {"reaction_time": 0.8, "lane_change_chance": 0.10, "follow_accuracy": 0.55, "max_speed": 5.6, "awareness_distance": 280, "avoidance_strength": 0.45, "panic_chance": 0.4},
    # Level 3: Player ~50s (212kph) -> Bot ~60s
    3: {"reaction_time": 0.6, "lane_change_chance": 0.15, "follow_accuracy": 0.70, "max_speed": 5.9, "awareness_distance": 360, "avoidance_strength": 0.60, "panic_chance": 0.3},
    # Level 4: Player ~45s (225kph) -> Bot ~55s
    4: {"reaction_time": 0.4, "lane_change_chance": 0.25, "follow_accuracy": 0.80, "max_speed": 6.1, "awareness_distance": 450, "avoidance_strength": 0.75, "panic_chance": 0.2},
    # Level 5: Player ~53s (200kph) -> Bot ~63s
    5: {"reaction_time": 0.3, "lane_change_chance": 0.35, "follow_accuracy": 0.90, "max_speed": 5.6, "awareness_distance": 520, "avoidance_strength": 0.85, "panic_chance": 0.1},
    # Level 6: High skill, very aware and aggressive
    6: {"reaction_time": 0.2, "lane_change_chance": 0.50, "follow_accuracy": 0.98, "max_speed": 6.5, "awareness_distance": 600, "avoidance_strength": 0.95, "panic_chance": 0.05},
}

from level1 import Level1Background
from level2 import Level2Background
from level3 import Level3Background
from level4 import Level4Background
from level5 import Level5Background
from level6 import Level6Background

# List of level classes for easy index-based access in Game class
LEVEL_CLASSES = [
    Level1Background,
    Level2Background,
    Level3Background,
    Level4Background,
    Level5Background,
    Level6Background
]

# Time taken and average speed references for balancing
"""
Level1: 50 seconds, 208 km/hr
Level2: 58 seconds, 197 km/hr
Level3: 50 seconds, 212 km/hr
Level4: 45 seconds, 225 km/hr
Level5: 53 seconds, 200 km/hr
"""

