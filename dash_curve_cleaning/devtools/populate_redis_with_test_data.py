"""
This script populates the Redis server with test data, useful to debug
the Dash app.
"""

import random

import redis


def generate_data(n_points, x_min, x_max, y_deviation, n_copies=10):
    x_original = [random.randint(x_min, x_max) for _ in range(n_points)]
    y_original = [x_ + random.randint(-y_deviation, y_deviation) for x_ in x_original]

    x = []
    y = []
    for _ in range(n_copies):
        x.extend(x_original)
        y.extend(y_original)

    return x, y


def generate_url(host, port, uuid, x_name, y_name, assets, point_groups, stages):
    point_groups_str = '&'.join([f"points_{i}={','.join(group)}" for i, group in enumerate(point_groups)])
    point_group_names = ','.join(f"points_{i}" for i, group in enumerate(point_groups))
    return f"http://{host}:{port}/dash?uuid={uuid}&assets={','.join(assets)}&x_name={x_name}&y_name={y_name}&{point_groups_str}&stages={','.join(stages)}&point_group_names={point_group_names}"


redis_cl = redis.Redis(
    # host=os.getenv('REDIS_HOST'),
    # port=int(os.getenv('REDIS_PORT')),
    # password=os.getenv('REDIS_PASSWORD'),
)

redis_cl.flushall()

### EXPERIMENT PARAMETERS ###
host = '0.0.0.0'
port = 8050
uuid = '12345'

n_points = 100
x_min = 0
x_max = 20
y_deviation = 2

x_name = 'active_power'
y_name = 'wind_speed'
assets = ['A01', 'A02', 'A03']
stages = ['original']

point_groups = (
    ('point_1', 'point_2', 'point_3'),
    ('point_4', 'point_5')
)
point_parameters = {
    'point_1': {
        'x': 0,
        'y': 0,
    },
    'point_2': {
        'x': 5,
        'y': 5,
    },
    'point_3': {
        'x': 10,
        'y': 5,
    },
    'point_4': {
        'x': 1,
        'y': 1,
    },
    'point_5': {
        'x': 3,
        'y': 1,
    },

}

for asset in assets:
    x, y = generate_data(n_points, x_min, x_max, y_deviation)
    redis_cl.rpush(f"{uuid}:{asset}:{x_name}:original", *x)
    redis_cl.rpush(f"{uuid}:{asset}:{y_name}:original", *y)

for point_name, parameters in point_parameters.items():
    redis_cl.mset(
        {
            f"{uuid}:{point_name}.x": parameters['x'],
            f"{uuid}:{point_name}.y": parameters['y'],
        }
    )

url = generate_url(host, port, uuid, x_name, y_name, assets, point_groups, stages)
print(url)
