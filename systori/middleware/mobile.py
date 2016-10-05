import re
import threading


FLAVOURS = ('full', 'mobile')
FLAVOURS_SESSION_KEY = 'flavour'
FLAVOURS_GET_PARAMETER = 'flavour'
DEFAULT_MOBILE_FLAVOUR = 'mobile'

_local = threading.local()


class SessionBackend:

    @staticmethod
    def get(request, default=None):
        return request.session.get(FLAVOURS_SESSION_KEY, default)

    @staticmethod
    def set(request, flavour):
        request.session[FLAVOURS_SESSION_KEY] = flavour

    @staticmethod
    def save(request, response):
        pass


flavour_storage = SessionBackend()


def get_flavour(request=None, default=None):
    flavour = None
    request = request or getattr(_local, 'request', None)
    # get flavour from storage if enabled
    if request:
        flavour = flavour_storage.get(request)
    # check if flavour is set on request
    if not flavour and hasattr(request, 'flavour'):
        flavour = request.flavour
    # if set out of a request-response cycle its stored on the thread local
    if not flavour:
        flavour = getattr(_local, 'flavour', default)
    # if something went wrong we return the very default flavour
    if flavour not in FLAVOURS:
        flavour = FLAVOURS[0]
    return flavour


def set_flavour(flavour, request=None, permanent=False):
    if flavour not in FLAVOURS:
        raise ValueError(
            u"'%r' is no valid flavour. Allowed flavours are: %s" % (
                flavour,
                ', '.join(FLAVOURS),))
    request = request or getattr(_local, 'request', None)
    if request:
        request.flavour = flavour
        if permanent:
            flavour_storage.set(request, flavour)
    elif permanent:
        raise ValueError(
            u'Cannot set flavour permanently, no request available.')
    _local.flavour = flavour


def _set_request_header(request, flavour):
    request.META['HTTP_X_FLAVOUR'] = flavour


def _init_flavour(request):
    _local.request = request
    if hasattr(request, 'flavour'):
        _local.flavour = request.flavour
    if not hasattr(_local, 'flavour'):
        _local.flavour = FLAVOURS[0]


class SetFlavourMiddleware(object):

    @staticmethod
    def process_request(request):
        _init_flavour(request)

        if FLAVOURS_GET_PARAMETER in request.GET:
            flavour = request.GET[FLAVOURS_GET_PARAMETER]
            if flavour in FLAVOURS:
                set_flavour(flavour, request, permanent=True)

    @staticmethod
    def process_response(request, response):
        flavour_storage.save(request, response)
        return response


class MobileDetectionMiddleware(object):
    user_agents_test_match = (
        "w3c ", "acs-", "alav", "alca", "amoi", "audi",
        "avan", "benq", "bird", "blac", "blaz", "brew",
        "cell", "cldc", "cmd-", "dang", "doco", "eric",
        "hipt", "inno", "ipaq", "java", "jigs", "kddi",
        "keji", "leno", "lg-c", "lg-d", "lg-g", "lge-",
        "maui", "maxo", "midp", "mits", "mmef", "mobi",
        "mot-", "moto", "mwbp", "nec-", "newt", "noki",
        "xda",  "palm", "pana", "pant", "phil", "play",
        "port", "prox", "qwap", "sage", "sams", "sany",
        "sch-", "sec-", "send", "seri", "sgh-", "shar",
        "sie-", "siem", "smal", "smar", "sony", "sph-",
        "symb", "t-mo", "teli", "tim-", "tosh", "tsm-",
        "upg1", "upsi", "vk-v", "voda", "wap-", "wapa",
        "wapi", "wapp", "wapr", "webc", "winw", "xda-",)
    user_agents_test_search = u"(?:%s)" % u'|'.join((
        'up.browser', 'up.link', 'mmp', 'symbian', 'smartphone', 'midp',
        'wap', 'phone', 'windows ce', 'pda', 'mobile', 'mini', 'palm',
        'netfront', 'opera mobi', 'android'
    ))
    user_agents_exception_search = u"(?:%s)" % u'|'.join((
        'ipad',
    ))
    http_accept_regex = re.compile("application/vnd\.wap\.xhtml\+xml", re.IGNORECASE)

    def __init__(self):
        user_agents_test_match = r'^(?:%s)' % '|'.join(self.user_agents_test_match)
        self.user_agents_test_match_regex = re.compile(user_agents_test_match, re.IGNORECASE)
        self.user_agents_test_search_regex = re.compile(self.user_agents_test_search, re.IGNORECASE)
        self.user_agents_exception_search_regex = re.compile(self.user_agents_exception_search, re.IGNORECASE)

    def process_request(self, request):
        is_mobile = False

        if 'HTTP_USER_AGENT' in request.META:
            user_agent = request.META['HTTP_USER_AGENT']

            # Test common mobile values.
            if self.user_agents_test_search_regex.search(user_agent) and \
                    not self.user_agents_exception_search_regex.search(user_agent):
                is_mobile = True
            else:
                if 'HTTP_ACCEPT' in request.META:
                    http_accept = request.META['HTTP_ACCEPT']
                    if self.http_accept_regex.search(http_accept):
                        is_mobile = True

            if not is_mobile:
                # Now we test the user_agent from a big list.
                if self.user_agents_test_match_regex.match(user_agent):
                    is_mobile = True

        if is_mobile:
            set_flavour(DEFAULT_MOBILE_FLAVOUR, request)
        else:
            set_flavour(FLAVOURS[0], request)
