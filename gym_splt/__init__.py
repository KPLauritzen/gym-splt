from gym.envs.registration import register

register(
    id='splt-v0',
    entry_point='gym_splt.envs.SpltEnv'
)