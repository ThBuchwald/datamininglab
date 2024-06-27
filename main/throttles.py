from rest_framework.throttling import SimpleRateThrottle

class GetRequestThrottle(SimpleRateThrottle):
    scope = 'get_requests'

    def get_cache_key(self, request, view):
        # Only throttle GET requests
        if request.method != 'GET':
            return None  # Do not throttle if not a GET request
        ident = self.get_ident(request)  # Get the unique identifier for the request
        return self.cache_format % {'scope': self.scope, 'ident': ident}

class PostRequestThrottle(SimpleRateThrottle):
    scope = 'post_requests'

    def get_cache_key(self, request, view):
        # Only throttle POST requests
        if request.method != 'POST':
            return None  # Do not throttle if not a POST request
        ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}

class PutDeleteRequestThrottle(SimpleRateThrottle):
    scope = 'write_requests'

    def get_cache_key(self, request, view):
        # Only throttle PUT and DELETE requests
        if request.method not in ['PUT', 'DELETE']:
            return None  # Do not throttle if not PUT or DELETE
        ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}