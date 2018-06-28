import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym_splt import core
import numpy as np

class SpltEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, width=8, height=16):
        self.width = width
        self.height = height
        self.board = core.Board(width=self.width, height=self.height)
        self.trans_buffer_state = {
            ' ':0, '*':0,
             '-':1, '|':1, 
             'p':1
             }
        self.state = self._get_state()
        self.n_actions = width * height
        self.action_space = spaces.Discrete(self.n_actions)
        self.observation_space = spaces.Box(low=0, high=1, shape=self.state.shape, dtype=np.uint8)

    def step(self, action):
        x = action % self.width
        y = action // self.width
        print(f'action: {action}, x: {x}, y: {y}')
        pre_score = self.board.score
        possible = split_x_y(self.board, x, y)

        # Check if move can be made
        if not possible:
            # Punish for making impossible moves
            self.board.score /= 2
        reward = self.board.score - pre_score
        self.state = self._get_state()

        # Check if we are done
        done = self._is_done()
        return (self.state, reward, done, {})

        

    def reset(self):
        self.board = core.Board(width=self.width, height=self.height)
        self.state = self._get_state()
        return self.state

    def render(self, mode='human', close=False):
        core.drawScreen(self.board)

    def _get_state(self):
        core.updateScreenBuffer(self.board)
        buffer = np.array(self.board.screenBuffer)
        state = np.zeros(shape=buffer.shape)
        state = np.vectorize(self.trans_buffer_state.get)(buffer)

        # Indicate parity
        if self.board.splitAction == '|':
            state[0,0] = 0
        else: 
            state[0,0] = 1

        return state

    def _is_done(self):
        move_options = self.board.getMoveOptions()
        if len(move_options) == 0:
            done = True
        else:
            done = False
        return done


def split_x_y(board, x, y):
    for boxindex, box in enumerate(board.box):
        if box.x <= x < (box.x + box.width):
            if box.y <= y < (box.y + box.height):
                return core.makeMove(board, boxindex)
    print('no split possible')
    return False
