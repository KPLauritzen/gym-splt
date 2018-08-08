import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym_splt import core
import numpy as np

translate_buffer_to_state = {
    core.NOPOINT:0, core.VOID:0,
    core.HORIZONTAL:1, core.VERTICAL:1, 
    'p':1
}
class SpltEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, width=8, height=16):
        self.width = width
        self.height = height
        self.board = core.Board(width=self.width, height=self.height)
        self.n_state_layers = 4
        self.state = self._get_state()
        self.n_actions = width * height
        self.action_space = spaces.Discrete(self.n_actions)
        self.observation_space = spaces.Box(low=0, high=1, shape=self.state.shape, dtype=np.uint8)
        self.time = 0

    def step(self, action):
        self.time += 1
        # Translate action to (x,y) coordinates
        x = action % self.width
        y = action // self.width
        #print(f'action: {action}, x: {x}, y: {y}')
        pre_score = self.board.score
        possible = split_x_y(self.board, x, y)

        # Check if move can be made
        if not possible:
            # Punish for making impossible moves
            #self.board.score -= 10
            pass
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
        # Layer 0: Void
        # Layer 1: log2(points)
        # Layer 2: Is wall on top?
        # Layer 3: Is wall on left?
        
        return state


    def _get_state_metadata(self, buffer=None):
        if buffer is None:
            buffer = np.array(self.board.screenBuffer)
        state = np.zeros(2)
        # Indicate parity
        if self.board.splitAction == core.VERTICAL:
            parity = 0
        else: 
            parity = 1
        state[0] = parity
        return state


    def _get_state(self):
        core.updateScreenBuffer(self.board)
        buffer = np.array(self.board.screenBuffer)
        board_state = self._get_board_state(buffer)
        meta_state = self._get_state_metadata()
        state = np.vectorize(translate_buffer_to_state.get)(buffer)

        # Indicate parity in top left corner
        if self.board.splitAction == core.VERTICAL:
            state[0,0] = 0
        else: 
            state[0,0] = 1

        return state.flatten()

    def _is_done(self):
        move_options = self.board.getMoveOptions()
        if len(move_options) == 0:
            # If there are no possible moves, the game is over
            done = True
        else:
            done = False
        return done


def split_x_y(board, x, y):
    for boxindex, box in enumerate(board.box):
        if box.x <= x < (box.x + box.width):
            if box.y <= y < (box.y + box.height):
                return core.makeMove(board, boxindex)
    #print('no split possible')
    return False
