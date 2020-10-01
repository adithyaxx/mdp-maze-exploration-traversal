def convert_long(distance):
    distance = float(distance)

    if 0 <= distance <= 11:
        return 0
    elif 11 < distance <= 17:
        return 1
    elif 17 < distance <= 27:
        return 2
    elif 27 < distance <= 37:
        return 3
    elif 37 < distance <= 47:
        return 4
    return 5


def convert_short(distance):
    distance = float(distance)

    if 0 <= distance <= 10:
        return 0
    elif 10 < distance <= 19:
        return 1
    elif 19 < distance <= 29:
        return 2
    return 3
