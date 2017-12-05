from channels.routing import route, include

channel_routing = [
    include('sisy.routing.channel_routing'),
#    route("websocket.connect", ws_add),
#    route("websocket.receive", ws_message),
#    route("websocket.disconnect", ws_disconnect),
]
