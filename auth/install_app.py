from base64 import b64encode
from os import urandom

from auth.models import App

if __name__ == '__main__':
    name = input('App Name: ')
    redirect = input('Redirect Url: ')
    if not redirect.startswith('https://'):
        raise ValueError('Redirect Url must starts with https')
    hash_secret = urandom(16)
    aead_secret = urandom(32)
    app = App.create(name=name, redirect=redirect, hash_secret=hash_secret, aead_secret=aead_secret)
    print('App ID: {}\nRedirect Url: {}\nSecret:\n{}'.format(app.name, app.redirect, b64encode(app.aead_secret)))
