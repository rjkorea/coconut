# -*- coding: utf-8 -*-

import re
import string
import random
import pbkdf2

HASHING_ITERATIONS = 400
ALLOWED_IN_SALT = string.ascii_letters + string.digits + './'
ALLOWD_ADMIN_PASSWORD_PATTERN = r'[A-Za-z0-9!@#$%^&+=]{8,}'
ALLOWD_USER_PASSWORD_PATTERN = r'[0-9]{4}'


def generate_random_string(len=12, allowed_chars=string.ascii_letters+string.digits):
    return ''.join(random.choice(allowed_chars) for i in range(len))


def make_password(password=None):
    if password is None:
        raise ValueError('password is required')
    salt = generate_random_string(len=32, allowed_chars=ALLOWED_IN_SALT)
    return pbkdf2.crypt(password, salt=salt, iterations=HASHING_ITERATIONS)


def check_password(password, hashed_password):
    return hashed_password == pbkdf2.crypt(password, hashed_password)


def validate_password(password=None):
    """
    ALLOWED_PASSWORD_PATTERN = r'[A-Za-z0-9!@#$%^&+=]{8,}'
    """
    if password is None:
        raise ValueError('password is required')
    if re.match(ALLOWD_ADMIN_PASSWORD_PATTERN, password):
        return True
    return False

def validate_user_password(password=None):
    """
    ALLOWED_PASSWORD_PATTERN = r'[A-Za-z0-9!@#$%^&+=]{4}'
    """
    if password is None:
        raise ValueError('password is required')
    if re.match(ALLOWD_USER_PASSWORD_PATTERN, password):
        return True
    return False
