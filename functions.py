import hashlib
import logging
import json
import multiprocessing as mp
from functools import partial
from tqdm import tqdm


def checking_hash(bin: int, config: dict, number: int) -> int:
    if hashlib.sha256(f'{bin}{number:06d}{config["last_digits"]}'.encode()).hexdigest() == f'{config["hash"]}':
        return int(f'{bin}{number:06d}{config["last_digits"]}')
    else:
        return False


def searching(config: dict, processes: int) -> None:
    flag = False
    with mp.Pool(processes) as p:
        for bin in config['first_digits']:
            logging.info(
                f'Search for a hash for a card {bin[:4]}-{bin[-2:]}XX-XXXX-{config["last_digits"]}')
            for result in p.map(partial(checking_hash, int(bin), config), tqdm(range(1000000))):
                if result:
                    p.terminate()
                    flag = True
                    logging.info(
                        f'The found card is on the way{ config["found_card"]}')
                    result_str = str(result)
                    logging.info(
                        f'The found card {result_str[:4]}-{result_str[4:8]}-{result_str[8:12]}-{result_str[12:]}')
                    data_tmp = {"card_number": f"{result}", "luhn_check": None}
                    try:
                        with open(config["found_card"], 'w') as f:
                            json.dump(data_tmp, f)
                    except FileNotFoundError:
                        logging.error(f"{config['found_card']} not found")
                    break
            if flag:
                break
    if not flag:
        logging.info('Card not found')


def luhn(config: dict) -> bool:
    try:
        with open(config["found_card"]) as f:
            found_card = json.load(f)
    except FileNotFoundError:
        logging.error(f"{config['found_card']} not found")
    number = str(found_card["card_number"])
    if not number.isdigit() or len(number) != 16:
        logging.info("The card number is incorrect")
        return False

    checksum = 0
    for i, digit in enumerate(reversed(number)):
        if i % 2 == 0:
            checksum += int(digit)
        else:
            checksum += sum(divmod(int(digit) * 2, 10))

    if checksum % 10 == 0:
        logging.info("The card is correct")
        return True
    else:
        logging.info("The card is incorrect")
        return False