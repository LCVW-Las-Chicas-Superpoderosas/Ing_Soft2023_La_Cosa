from load_data import load_cards
from model_base import initialize_database


if __name__ == '__main__':
    initialize_database()
    load_cards()
