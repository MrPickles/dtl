import logging
from datetime import timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def this_person_wants_to_play_league(msg: str) -> bool:
    keywords = ["sl", "dtl"]
    return (
        any(map(lambda x: x in msg[:-1].lower().split(" "), keywords))
        and msg[-1] == "?"
    )


def parse_timer(msg: str) -> Optional[timedelta]:
    in_split = msg.split(" in ")
    if len(in_split) != 2:
        logger.debug('No substring of "in" detected...')
        return None

    space_split = in_split[1].split(" ")
    if len(space_split) != 2:
        logger.debug("Time and unit wasn't split by a space")
        return None

    try:
        value = float(space_split[0])
    except ValueError as e:
        logger.debug("Numerical value failed to parse: %s", e)
        return None

    if value < 1:
        logger.debug("Duration is not positive: %s", value)
        return None

    full_unit = space_split[1]
    unit = full_unit[0].lower()
    if unit == "h" and value <= 3:
        return timedelta(hours=value)

    if unit == "m" and value >= 5:
        return timedelta(minutes=value)

    logger.debug(
        "Time unit didn't parse (%s) or value was out of bounds (%s)", full_unit, value
    )
    return None
