import random
import string


def generate_password():
    words = ['elf', 'santa', 'reindeer', 'snow']
    number = ''.join(random.choices(string.digits, k=2))
    password = ''.join(random.choice(words) + number)

    return password
