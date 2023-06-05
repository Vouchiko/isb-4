import logging
import argparse
import json
from functions import searching, luhn, get_stats

logger = logging.getLogger()
logger.setLevel('INFO')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hash Function Collision Search')
    parser.add_argument('mode', type=str, help='1 - Search for card numbers with a given hash '
                                               '2 - Checks the card for authenticity '
                                               '3 - Output of the dependence of the execution time on the number of '
                                               'threads')
    parser.add_argument('--config', type=str, help='Name of config file', default="Data/data.json")
    args = parser.parse_args()
    data_path = args.config

    try:
        with open(args.config, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"{args.config} not found")

    if args.mode == "1":
        logging.info('Search for the card number...\n')
        searching(data, int(data["processes_amount"]))
        logging.info('Card number search completed')
    elif args.mode == "2":
        logging.info('Checking the correctness of the card...')
        luhn(data)
        logging.info('Verification of the cards correctness is completed')
    elif args.mode == "3":
        logging.info('Data collection...\n')
        get_stats(data)
        logging.info('Data collection completed successfully \n')
    else:
        logging.error("Incorrect mode! Try again...")
