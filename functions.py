import hashlib
import logging
import json
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
from time import time
from matplotlib import pyplot as plt


def checking_hash(bin: int, config: dict, number: int) -> int:
    """
    Compares the hash of the received card with an existing one
    Parameters:
        bin(int): the first 6 digits of card
        config(dict): input data
        number(int): generated card digits
    Return value :
        (int): number, if the hash matches, otherwise False
    """
    if hashlib.sha256(f'{bin}{number:06d}{config["last_digits"]}'.encode()).hexdigest() == f'{config["hash"]}':
        return int(f'{bin}{number:06d}{config["last_digits"]}')
    else:
        return False


def searching(config: dict, processes: int) -> None:
    """
    Is looking for a card with the same hash
    Parameter:
        config(dict): input data
        processes(int): number of processes
    """
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
    """
    Checks the number for correctness by the luhn algorithm
    Parameters:
        config(dict): input data
    Return value:
        (bool): True if everything came together, otherwise - False
    """
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


def get_stats(config: dict) -> None:
    """
    Preserves the dependence of the hash collision search time on the number of processes
    Parameters:
        config(dict): input data
    """
    times = []
    for i in range(int(config["processes_amount"])):
        start = time()
        logging.info(f'number of processes: {i + 1}\n')
        searching(config, i + 1)
        times.append(time() - start)
    plt.figure(figsize=(30, 5))
    plt.ylabel('Time')
    plt.xlabel('Processes')
    plt.title('Time dependence on the number of processes')
    plt.plot(
        list(x + 1 for x in range(int(config["processes_amount"]))), times, color="blue")
    plt.savefig(f'{config["statistic_path"]}')
    logging.info(f'Time dependence on processes is preserved along the way {config["statistic_path"]}\n')



