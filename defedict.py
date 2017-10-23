import collections


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def defedict(components_to_use, components_order):
    newdict = {}

    for x in components_order:
        if x == 'position':
            newdict['position'] = (100, 100)
        elif x == 'rotate':
            newdict['rotate'] = 0
        elif x == 'renderer': 
            newdict['renderer'] = {'render': True}
        elif x == 'cymunk_physics':
            size = components_to_use['renderer']['size']
            pos = components_to_use.get('position', (100, 100))
            newdict['cymunk_physics'] = {
                        'main_shape': 'circle',
                        'velocity': (0, 0),
                        'angular_velocity': 0,
                        'angle': 0,
                        'vel_limit': float('inf'),
                        'ang_vel_limit': 0,
                        'mass': 50,
                        'position': pos,
                        'col_shapes': [{
                            'shape_type': 'circle',
                            'elasticity': 0.5,
                            'collision_type': 0,
                            'shape_info': {
                                'inner_radius': 0,
                                'outer_radius': size[0],
                                'mass': 50,
                                'offset': (0, 0)
                            },
                            'friction': 1.0
                        }],
                    }
        else:
            newdict[x] = {}

    update(newdict, components_to_use)
    return [newdict, components_order]
