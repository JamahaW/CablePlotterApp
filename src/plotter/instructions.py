__BEGIN_CODE = f"""
# BEGIN_CODE begin

.env esp32_env

# BEGIN_CODE end"""

__END_CODE = """
# END_CODE begin

exit

# END_CODE end"""

__MOVE_CODE = """move_to {x} {y}"""

__SET_SPEED = """set_motors_speed {speed}"""


def enc_code() -> str:
    return __END_CODE


def begin_code() -> str:
    return __BEGIN_CODE


def move_to(x: int, y: int) -> str:
    return __MOVE_CODE.format(x=x, y=y)


def set_motors_speed(speed: int) -> str:
    return __SET_SPEED.format(speed=speed)
