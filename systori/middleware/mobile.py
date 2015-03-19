from django_mobile.middleware import MobileDetectionMiddleware

class UbrMobileDetectionMiddleware(MobileDetectionMiddleware):
    user_agents_test_search = u"(?:%s)" % u'|'.join((
        'up.browser', 'up.link', 'mmp', 'symbian', 'smartphone', 'midp',
        'wap', 'phone', 'windows ce', 'pda', 'mobile', 'mini', 'palm',
        'netfront', 'opera mobi', 'android'
    ))