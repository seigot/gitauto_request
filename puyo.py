import pygame
import sys
import random
import time
import numpy as np
import pyttsx3
import math
from pygame.locals import *

# 初期化
pygame.init()
pygame.display.set_caption('ぷよぷよ通')

# 定数
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_WIDTH = 6
GRID_HEIGHT = 12
PUYO_SIZE = 32
BOARD_X = (SCREEN_WIDTH - PUYO_SIZE * GRID_WIDTH) // 2
BOARD_Y = 40

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
GRID_COLOR = (50, 50, 50)
BG_COLOR = (0, 0, 50)

# ぷよの色
PUYO_COLORS = [RED, GREEN, BLUE, YELLOW]
PUYO_COLOR_NAMES = {
    str(RED): "赤",
    str(GREEN): "緑",
    str(BLUE): "青",
    str(YELLOW): "黄"
}

# TTSエンジンの初期化
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# 連鎖ボイス
CHAIN_VOICES = {
    2: "ファイヤー",
    3: "アイスストーム",
    4: "ダイアキュート",
    5: "ばよえーん",
    6: "イレブンチェーン",
    7: "マジカルフィーバー",
    8: "ブレインダンプ",
    9: "ジュゲム",
    10: "バイオレットハイ",
    11: "ミラクルボンバー",
    12: "ファンタスティック"
}

# ゲーム画面の設定
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# 効果音の設定
try:
    drop_sound = pygame.mixer.Sound("drop.wav")  # 落下音
    rotate_sound = pygame.mixer.Sound("rotate.wav")  # 回転音
    chain_sound = pygame.mixer.Sound("chain.wav")  # 連鎖音
    pop_sound = pygame.mixer.Sound("pop.wav")  # 消去音
    has_sound = True
except:
    has_sound = False  # 音声ファイルがない場合

# ぷよぷよのクラス
class Puyo:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.falling = True
        self.connected = False
        self.checked = False

    def draw(self):
        pygame.draw.circle(screen, self.color, 
                          (BOARD_X + self.x * PUYO_SIZE + PUYO_SIZE // 2, 
                           BOARD_Y + self.y * PUYO_SIZE + PUYO_SIZE // 2), 
                          PUYO_SIZE // 2 - 2)
        pygame.draw.circle(screen, WHITE, 
                          (BOARD_X + self.x * PUYO_SIZE + PUYO_SIZE // 2 - 5, 
                           BOARD_Y + self.y * PUYO_SIZE + PUYO_SIZE // 2 - 5), 
                          PUYO_SIZE // 8)

# ぷよぷよのペアクラス
class PuyoPair:
    def __init__(self, x, grid):
        self.x = x
        self.y = 0
        self.rotation = 0  # 0: 上, 1: 右, 2: 下, 3: 左
        self.grid = grid
        self.colors = [random.choice(PUYO_COLORS), random.choice(PUYO_COLORS)]
        self.puyo1 = Puyo(x, 0, self.colors[0])
        self.puyo2 = Puyo(x, 1, self.colors[1])
    
    def rotate(self, direction):
        # 1: 時計回り, -1: 反時計回り
        old_rotation = self.rotation
        self.rotation = (self.rotation + direction) % 4
        
        # 回転後の位置をチェック
        if not self.can_rotate():
            # 回転できなければ元に戻す
            self.rotation = old_rotation
            return False
        
        # 回転音を再生
        if has_sound:
            rotate_sound.play()
            
        self.update_positions()
        return True
    
    def can_rotate(self):
        # 回転先の位置をチェック
        rot = self.rotation
        new_x1, new_y1 = self.x, self.y
        
        if rot == 0:  # 上
            new_x2, new_y2 = self.x, self.y + 1
        elif rot == 1:  # 右
            new_x2, new_y2 = self.x + 1, self.y
        elif rot == 2:  # 下
            new_x2, new_y2 = self.x, self.y + 1
        elif rot == 3:  # 左
            new_x2, new_y2 = self.x - 1, self.y
            
        # グリッド内にあるか
        if (new_x1 < 0 or new_x1 >= GRID_WIDTH or new_y1 < 0 or new_y1 >= GRID_HEIGHT or
            new_x2 < 0 or new_x2 >= GRID_WIDTH or new_y2 < 0 or new_y2 >= GRID_HEIGHT):
            return False
            
        # 他のぷよと重ならないか
        if (self.grid[new_y1][new_x1] is not None or self.grid[new_y2][new_x2] is not None):
            return False
            
        return True
    
    def update_positions(self):
        if self.rotation == 0:  # 上
            self.puyo1.x = self.x
            self.puyo1.y = self.y
            self.puyo2.x = self.x
            self.puyo2.y = self.y + 1
        elif self.rotation == 1:  # 右
            self.puyo1.x = self.x
            self.puyo1.y = self.y
            self.puyo2.x = self.x + 1
            self.puyo2.y = self.y
        elif self.rotation == 2:  # 下
            self.puyo1.x = self.x
            self.puyo1.y = self.y + 1
            self.puyo2.x = self.x
            self.puyo2.y = self.y
        elif self.rotation == 3:  # 左
            self.puyo1.x = self.x
            self.puyo1.y = self.y
            self.puyo2.x = self.x - 1
            self.puyo2.y = self.y
    
    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 移動先がグリッド内にあるか確認
        if self.can_move(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.update_positions()
            return True
        return False
        
    def drop_to_bottom(self):
        # 一番下まで落とす（ちぎり機能）
        while self.move(0, 1):
            pass
    
    def can_move(self, new_x, new_y):
        rot = self.rotation
        # 上
        if rot == 0:
            if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y + 1 >= GRID_HEIGHT:
                return False
            if self.grid[new_y][new_x] is not None or self.grid[new_y + 1][new_x] is not None:
                return False
        # 右
        elif rot == 1:
            if new_x < 0 or new_x + 1 >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                return False
            if self.grid[new_y][new_x] is not None or self.grid[new_y][new_x + 1] is not None:
                return False
        # 下
        elif rot == 2:
            if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y + 1 >= GRID_HEIGHT:
                return False
            if self.grid[new_y][new_x] is not None or self.grid[new_y + 1][new_x] is not None:
                return False
        # 左
        elif rot == 3:
            if new_x - 1 < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                return False
            if self.grid[new_y][new_x] is not None or self.grid[new_y][new_x - 1] is not None:
                return False
        return True

    def draw(self):
        self.puyo1.draw()
        self.puyo2.draw()

# ゲームクラス
class PuyoGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_pair = self.create_new_pair()
        self.next_pair = self.create_new_pair()
        self.fall_time = 0
        self.fall_speed = 0.5  # ぷよが1マス落ちる時間（秒）
        self.game_over = False
        self.score = 0
        self.chain_count = 0
        self.falling_puyos = False
        self.last_key_time = 0
        self.key_delay = 0.15  # キー入力の遅延（秒）
        self.last_rotation_time = 0
        self.rotation_delay = 0.25  # 回転の遅延（秒）
        self.pop_effects = []  # 消去エフェクト（星など）
        self.effect_duration = 1.0  # エフェクトの持続時間（秒）
        self.puyo_pop_state = {}  # ぷよの消去状態を管理
    
    def create_new_pair(self):
        return PuyoPair(GRID_WIDTH // 2 - 1, self.grid)
    
    def add_puyos_to_grid(self, puyo1, puyo2):
        if 0 <= puyo1.y < GRID_HEIGHT and 0 <= puyo1.x < GRID_WIDTH:
            self.grid[puyo1.y][puyo1.x] = puyo1
        if 0 <= puyo2.y < GRID_HEIGHT and 0 <= puyo2.x < GRID_WIDTH:
            self.grid[puyo2.y][puyo2.x] = puyo2
            
        # 横に置いた場合、下が空いていれば落とす処理
        self.handle_floating_puyos()
    
    def handle_floating_puyos(self):
        # 横に置いて空中に浮いている状態のぷよを落とす
        puyo_dropped = True
        
        while puyo_dropped:
            puyo_dropped = False
            for y in range(GRID_HEIGHT - 2, -1, -1):
                for x in range(GRID_WIDTH):
                    if self.grid[y][x] is not None and self.grid[y + 1][x] is None:
                        # 下が空いている場合は落とす
                        self.grid[y + 1][x] = self.grid[y][x]
                        self.grid[y + 1][x].y = y + 1
                        self.grid[y][x] = None
                        puyo_dropped = True
    
    def check_game_over(self):
        # 上部の行に固定されたぷよがあるかチェック
        if self.grid[1][GRID_WIDTH // 2 - 1] is not None or self.grid[1][GRID_WIDTH // 2] is not None:
            self.game_over = True
            
    def quick_drop(self):
        # ちぎり機能（一番下まで落とす）
        if not self.falling_puyos and not self.game_over:
            self.current_pair.drop_to_bottom()
            
            # ドロップ音を再生
            if has_sound:
                drop_sound.play()
                
            # 固定する
            self.add_puyos_to_grid(self.current_pair.puyo1, self.current_pair.puyo2)
            # 連鎖チェック
            if not self.check_matches():
                self.current_pair = self.next_pair
                self.next_pair = self.create_new_pair()
                self.check_game_over()
    
    def check_matches(self):
        # 全てのぷよのcheckedフラグをリセット
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    self.grid[y][x].checked = False
        
        groups = []
        # 4つ以上連結したぷよを探す
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None and not self.grid[y][x].checked:
                    group = self.find_connected_puyos(x, y, self.grid[y][x].color)
                    if len(group) >= 4:
                        groups.append(group)
        
        # 連鎖があればぷよを消して得点計算
        if groups:
            self.chain_count += 1
            total_cleared = 0
            
            # 連鎖ボイスの再生
            if self.chain_count in CHAIN_VOICES:
                self.play_chain_voice(self.chain_count)
            
            # ぷよを消す&エフェクトを追加
            for group in groups:
                total_cleared += len(group)
                for puyo in group:
                    # ぷよの消去状態を作成
                    puyo_key = f"{puyo.x},{puyo.y}"
                    self.puyo_pop_state[puyo_key] = {
                        "x": puyo.x,
                        "y": puyo.y,
                        "color": puyo.color,
                        "time": self.effect_duration,
                        "scale": 1.0,
                        "chain": self.chain_count,
                        "original_puyo": puyo,
                        "brightness": 0.0,  # 輝度（0.0〜1.0）
                        "phase": 0.0  # アニメーションフェーズ
                    }
                    
                    # エフェクトを作成
                    self.pop_effects.append({
                        "x": puyo.x,
                        "y": puyo.y,
                        "color": puyo.color,
                        "time": self.effect_duration,
                        "radius": PUYO_SIZE // 2,
                        "chain": self.chain_count  # 連鎖数を保存
                    })
                    
                    # グリッドから削除
                    self.grid[puyo.y][puyo.x] = None
                    
            # 消去音を再生
            if has_sound:
                pop_sound.play()
            
            # 得点計算
            chain_power = min(999, self.chain_count * 2)
            group_bonus = min(999, len(groups) - 1)
            connection_bonus = 0
            for group in groups:
                connection_bonus += min(999, (len(group) - 4) * 1)
            
            score_formula = 10 * total_cleared * max(1, chain_power + group_bonus + connection_bonus)
            self.score += score_formula
            
            # ぷよを落とす
            self.falling_puyos = True
            return True
        else:
            self.chain_count = 0
            return False
    
    def find_connected_puyos(self, x, y, color):
        if (y < 0 or y >= GRID_HEIGHT or x < 0 or x >= GRID_WIDTH or 
                self.grid[y][x] is None or self.grid[y][x].checked or 
                self.grid[y][x].color != color):
            return []
        
        self.grid[y][x].checked = True
        result = [self.grid[y][x]]
        
        # 上下左右を確認
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in directions:
            result.extend(self.find_connected_puyos(x + dx, y + dy, color))
        
        return result
    
    def fall_puyos(self):
        moved = False
        for y in range(GRID_HEIGHT - 2, -1, -1):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None and self.grid[y + 1][x] is None:
                    self.grid[y + 1][x] = self.grid[y][x]
                    self.grid[y + 1][x].y = y + 1
                    self.grid[y][x] = None
                    moved = True
        return moved
    
    def play_chain_voice(self, chain_count):
        if chain_count in CHAIN_VOICES:
            voice = CHAIN_VOICES[chain_count]
            tts_engine.say(voice)
            tts_engine.runAndWait()
            
            # 連鎖音を再生
            if has_sound:
                chain_sound.play()
    
    def handle_input(self, keys):
        if self.falling_puyos or self.game_over:
            return
        
        # キー入力の制限時間を設ける
        current_time = time.time()
        if current_time - self.last_key_time < self.key_delay:
            return
        
        # 回転に時間がかかるようにする
        if current_time - self.last_rotation_time < self.rotation_delay and (keys[K_UP] or keys[K_z] or keys[K_x]):
            return
            
        moved = False
        if keys[K_LEFT]:
            moved = self.current_pair.move(-1, 0)
        elif keys[K_RIGHT]:
            moved = self.current_pair.move(1, 0)
        elif keys[K_DOWN]:
            moved = self.current_pair.move(0, 1)
        elif keys[K_UP]:  # 上キーに変更
            moved = self.current_pair.rotate(1)  # 回転
            if moved:
                self.last_rotation_time = current_time
        elif keys[K_z]:
            moved = self.current_pair.rotate(-1)  # 反時計回り
            if moved:
                self.last_rotation_time = current_time
        elif keys[K_x]:
            moved = self.current_pair.rotate(1)   # 時計回り
            if moved:
                self.last_rotation_time = current_time
        elif keys[K_c]:  # Cキーでちぎり（強制落下）
            self.quick_drop()
            moved = True
            
        if moved:
            self.last_key_time = current_time
    
    def update(self, dt):
        if self.game_over:
            return
        
        # ぷよの消去アニメーション更新
        for key, pop_state in list(self.puyo_pop_state.items()):
            pop_state["time"] -= dt
            
            # 全体の進行度（0.0〜1.0）
            progress = 1.0 - (pop_state["time"] / self.effect_duration)
            pop_state["phase"] = progress
            
            # ぷよっと感を出すためのアニメーション（膨らんでから縮む）
            if progress < 0.3:  # 最初の30%で膨らむ
                pop_state["scale"] = 1.0 + (progress / 0.3) * 0.5  # 最大1.5倍まで膨らむ
                # 明るくなっていく（0.0〜0.7）
                pop_state["brightness"] = progress / 0.3 * 0.7
            elif progress < 0.7:  # 30%〜70%は明るく輝く
                pop_state["scale"] = 1.5 - ((progress - 0.3) / 0.4) * 0.5  # 1.5倍から1.0倍に
                # 完全に明るく（0.7〜1.0）
                pop_state["brightness"] = 0.7 + (progress - 0.3) / 0.4 * 0.3
            else:  # 残り30%で縮んでいく
                pop_state["scale"] = 1.0 - ((progress - 0.7) / 0.3)  # 1.0倍から0倍に縮む
                # 明るさ最大
                pop_state["brightness"] = 1.0
            
            if pop_state["time"] <= 0:
                del self.puyo_pop_state[key]
        
        # エフェクトの更新
        for effect in self.pop_effects[:]:
            effect["time"] -= dt
            if effect["time"] <= 0:
                self.pop_effects.remove(effect)
            else:
                # エフェクトサイズを時間経過で拡大
                progress = 1.0 - (effect["time"] / self.effect_duration)
                if progress < 0.7:  # 最初の70%で徐々に大きく
                    effect["radius"] = PUYO_SIZE // 2 * (1 + progress * 2)
                else:  # 残り30%で一気に拡大
                    effect["radius"] = PUYO_SIZE // 2 * (1 + progress * 4)
        
        if self.falling_puyos:
            if not self.fall_puyos():
                self.falling_puyos = False
                # 落下が終わったら再度連鎖をチェック
                if not self.check_matches():
                    # 連鎖がなければ新しいぷよぺアを生成
                    self.current_pair = self.next_pair
                    self.next_pair = self.create_new_pair()
                    self.check_game_over()
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.current_pair.move(0, 1):
                # 移動できなければ固定する
                self.add_puyos_to_grid(self.current_pair.puyo1, self.current_pair.puyo2)
                # 連鎖チェック
                if not self.check_matches():
                    self.current_pair = self.next_pair
                    self.next_pair = self.create_new_pair()
                    self.check_game_over()
    
    def draw(self):
        # 背景を描画
        screen.fill(BG_COLOR)
        
        # グリッドの描画
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pygame.draw.rect(screen, GRID_COLOR, 
                                (BOARD_X + x * PUYO_SIZE, BOARD_Y + y * PUYO_SIZE, 
                                 PUYO_SIZE, PUYO_SIZE), 1)
        
        # グリッド上のぷよを描画
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    self.grid[y][x].draw()
        
        # 消去中のぷよを描画（点灯しながら消える）
        for key, pop_state in self.puyo_pop_state.items():
            # 時間に基づいて透明度を計算
            alpha = int(255 * (pop_state["time"] / self.effect_duration))
            
            # 元の色を取得
            base_color = pop_state["color"][:3]
            
            # 明るさに基づいて色を変更（白に近づける）
            brightness = pop_state["brightness"]
            color = tuple([min(255, int(c * (1 - brightness) + 255 * brightness)) for c in base_color])
            color_with_alpha = (*color, alpha)
            
            # 現在のサイズを計算
            current_radius = int(PUYO_SIZE // 2 * pop_state["scale"])
            
            # 点灯するぷよを描画
            if current_radius > 0:
                s = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, color_with_alpha, (current_radius, current_radius), current_radius)
                
                # 白い光沢も拡大縮小に合わせる
                highlight_radius = max(1, int(PUYO_SIZE // 8 * pop_state["scale"]))
                highlight_offset = max(1, int(5 * pop_state["scale"]))
                pygame.draw.circle(s, (255, 255, 255, alpha), 
                                (current_radius - highlight_offset, current_radius - highlight_offset), 
                                highlight_radius)
                
                # 連鎖数に応じた輝きエフェクト
                chain = pop_state.get("chain", 1)
                if chain > 1 and pop_state["brightness"] > 0.5:
                    # 内側から外側に広がる輝きの輪
                    glow_phases = [0.3, 0.6, 0.9]  # 複数の輝きの位相
                    for glow_phase in glow_phases:
                        # 位相に基づいてサイズを計算（膨張と収縮を繰り返す）
                        phase_offset = (pop_state["phase"] * 3 + glow_phase) % 1.0
                        glow_size = current_radius * (0.6 + phase_offset * 0.8)
                        
                        if glow_size > 0:
                            # 連鎖数に応じた色
                            if chain <= 3:
                                glow_color = (255, 255, 100, int(alpha * 0.5 * (1 - phase_offset)))
                            elif chain <= 5:
                                glow_color = (255, 100, 255, int(alpha * 0.5 * (1 - phase_offset)))
                            else:
                                glow_color = (100, 255, 255, int(alpha * 0.5 * (1 - phase_offset)))
                                
                            # 輝きの輪を描画
                            pygame.draw.circle(s, glow_color, (current_radius, current_radius), 
                                            glow_size, max(1, int(current_radius * 0.15)))
                
                # 画面に描画
                x, y = pop_state["x"], pop_state["y"]
                center_x = BOARD_X + x * PUYO_SIZE + PUYO_SIZE // 2
                center_y = BOARD_Y + y * PUYO_SIZE + PUYO_SIZE // 2
                screen.blit(s, (center_x - current_radius, center_y - current_radius))
        
        # エフェクトを描画
        for effect in self.pop_effects:
            # 透明度を時間に基づいて変更
            alpha = int(255 * effect["time"] / self.effect_duration)
            
            # 連鎖数を取得（デフォルトは1）
            chain = effect.get("chain", 1)
            
            # 星形のエフェクトを追加 - 連鎖数が高いほど多く、大きく
            if effect["time"] > self.effect_duration * 0.5 and chain > 1:
                s = pygame.Surface((effect["radius"] * 2, effect["radius"] * 2), pygame.SRCALPHA)
                
                star_count = 1 + (chain - 1) // 2  # 連鎖数に応じて星の数を増やす
                for i in range(star_count):
                    # 星の内部 - 連鎖数に応じて色を変える
                    star_colors = [
                        (255, 255, 0, alpha),  # 黄色
                        (255, 0, 255, alpha),  # マゼンタ
                        (0, 255, 255, alpha),  # シアン
                        (255, 165, 0, alpha),  # オレンジ
                    ]
                    star_color = star_colors[(chain + i) % len(star_colors)]
                        
                    # 星のサイズと位置を計算
                    # 星のサイズと位置を計算
                    star_size = effect["radius"] * 0.6
                    angle = (i * 360 / star_count) * 3.14159 / 180
                    offset_x = math.cos(angle) * effect["radius"] * 0.5
                    offset_y = math.sin(angle) * effect["radius"] * 0.5
                    center_x = effect["radius"] + offset_x
                    center_y = effect["radius"] + offset_y
                    
                    # 星を描画
                    points = []
                    for j in range(8):
                        point_angle = (j * 45 + 22.5 * (i % 2)) * 3.14159 / 180
                        dist = star_size if j % 2 == 0 else star_size * 0.4
                        points.append((
                            center_x + math.cos(point_angle) * dist,
                            center_y + math.sin(point_angle) * dist
                        ))
                    pygame.draw.polygon(s, star_color, points)
                
                screen.blit(s, (BOARD_X + effect["x"] * PUYO_SIZE + PUYO_SIZE // 2 - effect["radius"], 
                            BOARD_Y + effect["y"] * PUYO_SIZE + PUYO_SIZE // 2 - effect["radius"]))
        
        # 現在のぷよペアを描画
        if not self.falling_puyos and not self.game_over:
            self.current_pair.draw()
        
        # 次のぷよペアを表示
        font = pygame.font.Font(None, 24)
        next_text = font.render("NEXT", True, WHITE)
        screen.blit(next_text, (SCREEN_WIDTH - 100, 50))
        
        pygame.draw.circle(screen, self.next_pair.colors[0], 
                          (SCREEN_WIDTH - 70, 90), 
                          PUYO_SIZE // 2 - 2)
        pygame.draw.circle(screen, WHITE, 
                          (SCREEN_WIDTH - 75, 85), 
                          PUYO_SIZE // 8)
        
        pygame.draw.circle(screen, self.next_pair.colors[1], 
                          (SCREEN_WIDTH - 70, 130), 
                          PUYO_SIZE // 2 - 2)
        pygame.draw.circle(screen, WHITE, 
                          (SCREEN_WIDTH - 75, 125), 
                          PUYO_SIZE // 8)
        
        # スコアの表示
        score_text = font.render(f"SCORE: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # 連鎖数の表示
        if self.chain_count > 0:
            chain_text = font.render(f"{self.chain_count} れんさ!", True, WHITE)
            screen.blit(chain_text, (SCREEN_WIDTH // 2 - 50, 10))
        
        # 操作方法の表示
        controls_font = pygame.font.Font(None, 18)
        controls = [
            "方向キー: 移動・回転",
            "Z/X: 回転",
            "C: ちぎり（一気に落とす）",
            "R: リスタート"
        ]
        for i, control in enumerate(controls):
            control_text = controls_font.render(control, True, WHITE)
            screen.blit(control_text, (10, SCREEN_HEIGHT - 80 + i * 20))
            
        # ゲームオーバー表示
        if self.game_over:
            game_over_font = pygame.font.Font(None, 48)
            game_over_text = game_over_font.render("GAME OVER", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 24))
            
            restart_font = pygame.font.Font(None, 24)
            restart_text = restart_font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20))

# メイン関数
def main():
    game = PuyoGame()
    last_time = time.time()
    
    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_r and game.game_over:
                    game.reset()
        
        # 入力処理
        keys = pygame.key.get_pressed()
        game.handle_input(keys)
        
        # ゲーム状態の更新
        game.update(dt)
        
        # 描画
        game.draw()
        
        # 画面の更新
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()