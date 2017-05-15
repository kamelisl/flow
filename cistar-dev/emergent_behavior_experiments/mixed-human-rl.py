''' Script used for running case with mixed number of OVM cars and RL cars
operating on the SimpleEmission environment '''

import logging

from rllab.envs.normalized_env import normalize
from rllab.misc.instrument import stub, run_experiment_lite
from rllab.algos.trpo import TRPO
from rllab.baselines.linear_feature_baseline import LinearFeatureBaseline
from rllab.policies.gaussian_mlp_policy import GaussianMLPPolicy

# from cistar.core.exp import SumoExperiment
from cistar.envs.loop_accel import SimpleAccelerationEnvironment
from cistar.envs.loop_accel_pos_vel import ExtendedAccelerationEnvironment
from cistar.envs.loop_emission import SimpleEmissionEnvironment
from cistar.scenarios.loop.loop_scenario import LoopScenario
from cistar.controllers.rlcontroller import RLController
from cistar.controllers.lane_change_controllers import *
from cistar.controllers.car_following_models import *

logging.basicConfig(level=logging.INFO)

stub(globals())

sumo_params = {"time_step":0.01}
sumo_binary = "sumo"

env_params = {"target_velocity": 8, "max-deacc": -3, "max-acc": 3, "fail-safe": 'instantaneous'}

net_params = {"length": 230, "lanes": 1, "speed_limit": 35, "resolution": 40,
              "net_path": "debug/rl/net/"}

cfg_params = {"start_time": 0, "end_time": 3000, "cfg_path": "debug/rl/cfg/"}

initial_config = {"shuffle": False}

num_cars = 22
num_auto = 1

exp_tag = str(num_cars) + 'emissioncost-nofueld'

type_params = {"rl":(num_auto, (RLController, {}), (StaticLaneChanger, {}), 0), 
               "ovm": (num_cars - num_auto, (OVMController, {}), (StaticLaneChanger, {}), 0)}

scenario = LoopScenario(exp_tag, type_params, net_params, cfg_params, initial_config=initial_config)

env = SimpleEmissionEnvironment(env_params, sumo_binary, sumo_params, scenario)

env = normalize(env)

for seed in [16, 20, 21, 22]:
    policy = GaussianMLPPolicy(
        env_spec=env.spec,
        hidden_sizes=(32,32)
    )

    baseline = LinearFeatureBaseline(env_spec=env.spec)

    algo = TRPO(
        env=env,
        policy=policy,
        baseline=baseline,
        batch_size=300,
        max_path_length=15,
        n_itr=1,  # 1000
        # whole_paths=True,
        discount=0.999,
        step_size=0.01,
    )
    # algo.train()

    run_experiment_lite(
        algo.train(),
        # Number of parallel workers for sampling
        n_parallel=8,
        # Only keep the snapshot parameters for the last iteration
        snapshot_mode="all",
        # Specifies the seed for the experiment. If this is not provided, a random seed
        # will be used
        seed=seed,
        mode="local_docker",
        #mode="ec2",
        exp_prefix=exp_tag
        # plot=True,
    )