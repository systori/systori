from channels.routing import ProtocolTypeRouter

application = ProtocolTypeRouter({
    # (http->django views are added by default)
})