import socketio

sio = socketio.Client()

def connect_ws(server_url: str, auth_token: str):
    ''' Connect to the server '''
    sio.connect(server_url, auth={'token': auth_token}, socketio_path='/ws/socket.io', namespaces=['/worker'])
    return sio
