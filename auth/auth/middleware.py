class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, env, start_response):

        if env['PATH_INFO'].startswith(self.prefix):
            env['PATH_INFO'] = env['PATH_INFO'][len(self.prefix):]
            env['SCRIPT_NAME'] = self.prefix
            return self.app(env, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ['This url does not belong to the app.'.encode()]
