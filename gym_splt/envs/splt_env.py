import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym_splt import core
import numpy as np
from math import log2

translate_buffer_to_state = {
    core.NOPOINT: 0, core.VOID: -1,
    core.HORIZONTAL: 1, core.VERTICAL: 1, 
    'p': 1
}


class SpltEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, width=4, height=8, max_time=500):
        self.width = width
        self.height = height
        self.board = core.Board(width=self.width, height=self.height)
        self.n_state_layers = 5
        self.state = self._get_state() 
        self.n_actions = width * height
        self.action_space = spaces.Discrete(self.n_actions)
        self.observation_space = spaces.Box(low=0, high=15, 
            shape=self.state.shape, dtype=np.uint8)
        self.time = 0
        self.max_time = max_time
        self.penalty_impossible = 1

    def step(self, action):
        self.time += 1
        # Translate action to (x,y) coordinates
        x = action % self.width
        y = action // self.width
        pre_score = self.board.score
        possible = split_x_y(self.board, x, y)

        # Check if move can be made
        if not possible:
            # Punish for making impossible moves
            self.board.score -= self.penalty_impossible
        reward = self.board.score - pre_score
        self.state = self._get_state()

        # Check if we are done
        done = self._is_done()
        return (self.state, reward, done, {})

    def reset(self):
        self.board = core.Board(width=self.width, height=self.height)
        self.state = self._get_state()
        self.time = 0
        return self.state

    def render(self, mode='human', close=False):
        core.drawScreen(self.board)

    def _get_board_state(self, buffer=None):
        if buffer is None:
            buffer = np.array(self.board.screenBuffer)

        state = np.zeros(shape=(self.n_state_layers, self.height, self.width))

        top_walls = buffer[:-2:2, 1::2]
        side_walls = buffer[1::2, 2::2]
        insides = buffer[1::2, 1::2]
        # Layer 0: Void
        is_void = np.zeros(shape=(self.height, self.width))
        void_mask = insides == core.VOID
        is_void[void_mask] = 1
        state[0] = is_void
        # Layer 1: log2(points)
        log_points = np.ones(shape=(self.height, self.width))
        nopoint_mask = insides == core.NOPOINT
        log_points[~void_mask & ~nopoint_mask] = insides[~void_mask & ~nopoint_mask]
        log_points = np.log2(log_points)
        state[1] = log_points
        # Layer 2: Is wall on top?
        top = np.zeros(shape=(self.height, self.width))
        top_mask = top_walls != ' ' # If not a space, it is a wall
        top[top_mask] = 1
        state[2] = top
        # Layer 3: Is wall on left?
        side = np.zeros(shape=(self.height, self.width))
        side_mask = side_walls != ' ' # If not a space, it is a wall
        side[side_mask] = 1
        state[3] = side
        # Layer 4: metadata - game length, vert/horizontal parity
        metadata = self._get_state_metadata()
        state[4, 0, :2] = metadata

        return state

    def _get_state_metadata(self):
        # Indicate parity
        if self.board.splitAction == core.VERTICAL:
            parity = 0
        else: 
            parity = 1
        # How many legal moves have been done?
        game_length = len(self.board.splitRecord) + 1
        log2_game_length = np.log2(game_length)
        # Add to array
        state = np.zeros(2)
        state[0] = parity
        state[1] = log2_game_length
        return state

    def _get_state(self):
        core.updateScreenBuffer(self.board)
        buffer = np.array(self.board.screenBuffer)
        board_state = self._get_board_state(buffer)

        return board_state

    def _is_done(self):
        move_options = self.board.getMoveOptions()
        if len(move_options) == 0:
            # If there are no possible moves, the game is over
            done = True
        elif self.time > self.max_time:
            # We have taken more move attempts than max_time
            done = True
        else:
            done = False
        return done


def split_x_y(board, x, y):
    for boxindex, box in enumerate(board.box):
        if box.x <= x < (box.x + box.width):
            if box.y <= y < (box.y + box.height):
                return core.makeMove(board, boxindex)
    return False
