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


def convert_to_cm_long(units):
    if units == 0:
        return 11
    elif units == 1:
        return 17
    elif units == 2:
        return 27
    elif units == 3:
        return 37
    elif units == 4:
        return 47
    return 57


def convert_to_cm_short(units):
    if units == 0:
        return 10
    elif units == 1:
        return 19
    elif units == 2:
        return 29
    return 39
