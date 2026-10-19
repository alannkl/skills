import logging

log = logging.getLogger(__name__)


def create_charge(card_number: str) -> None:
    log.info("charge requested: card=%s", card_number[-4:])
