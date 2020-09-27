def convert_long(distance):
    distance = float(distance)

    if 0 <= distance <= 9:
        return 0
    elif 9 < distance <= 21:
        return 1
    elif 21 < distance <= 32:
        return 2
    elif 32 < distance <= 44:
        return 3
    elif 44 < distance <= 54:
        return 4
    elif 54 < distance <= 61:
        return 5
    return 6


def convert_short(distance):
    distance = float(distance)

    if 0 <= distance <= 10:
        return 0
    elif 10 < distance <= 19:
        return 1
    elif 19 < distance <= 29:
        return 2
    return 3
