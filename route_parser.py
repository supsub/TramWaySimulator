def parse_route(path = 'resources/trasa'):
    stops = []
    with open(path, 'r') as f:
        stops = f.readlines()

    result = []
    for stop in stops:
        splitted = stop.rsplit()
        result.append(" ".join(splitted))

    open('resources/trasa', 'w').close()

    parsed = []

    with open('resources/trasa', 'w') as f:
        for item in result:
            parsed.append(item)

    return parsed