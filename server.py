import socket
import json
from pymongo import MongoClient

#########         CONNECT TO MONGODB ATLAS       ############
#########                 DEF FUNCTION           ###########
client = MongoClient(
    "mongodb+srv://nguyentran186:tkbd1752003@printer-db.3x2fjj1.mongodb.net/?retryWrites=true&w=majority")
db = client.get_database('CN')
records = db.Client_Info


def SEND_request(client_name, path, filename):
    new_document = {
        "client_name": client_name,
        "path": path,
        "file_name": filename
    }
    records.insert_one(new_document)
    return


def ADD_request_(request):
    if records.count_documents({
        "client_name": client_name,
        "file_name": request[1]
    }) > 0:
        client_conn.send('Document existed'.encode())
    else:
        SEND_request(client_name, request[0], request[1])
        client_conn.send('Add info sucessful'.encode())


def REMOVE_request(clientname, filename):
    remove_query = {"$and": [
        {"file_name": filename},
        {"client_name": clientname}
    ]}

    records.delete_one(remove_query)
    return


def REMOVE_request_(request):
    if records.count_documents({
        "client_name": client_name,
        "file_name": request[0]
    }) == 0:
        client_conn.send('Document does not existed'.encode())
    else:
        REMOVE_request(client_name, request[0])
        client_conn.send('Remove sucessful'.encode())


def UPDATE_request(clientname, newpath, filename):
    update_query = {"$and": [
        {"file_name": filename},
        {"client_name": clientname}
    ]}
    newvalues = {"$set": {"path": newpath}}
    records.update_one(update_query, newvalues)
    return


def FETCH_request(request):
    if records.count_documents({
        "file_name": request[0]
    }) == 0:
        client_conn.send('Document does not existed'.encode())
    else:
        data = {"client": []}
        file_list = records.find({"file_name": request[0]}, {'_id': 0})
        for file in file_list:
            data['client'].append(file)
        client_conn.send(json.dumps(data).encode())


def UPDATE_request_(request):
    if records.count_documents({
        "client_name": client_name,
        "file_name": request[1]
    }) == 0:
        client_conn.send('Document does not existed'.encode())
    else:
        UPDATE_request(client_name, request[0], request[1])
        client_conn.send('Update sucessful'.encode())


def GET_request_():
    if records.count_documents({
        "client_name": client_name
    }) == 0:
        client_conn.send('-1'.encode())
    else:
        data = {"client_info": []}
        file_list = records.find({"client_name": client_name}, {'_id': 0})
        for file in file_list:
            data['client_info'].append(file)
        print(data)
        client_conn.send(json.dumps(data).encode())


#########         SETTING      ###################
##################################################
server_ip = socket.gethostbyname(socket.gethostname())
server_port = 23578

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))

#############      LISTENING     ################
#################################################
while True:
    print(f"Server is listening with IP address: {server_ip} on port: {server_port}")
    server.listen()
    client_conn, client_addr = server.accept()
    client_name = client_conn.recv(2048).decode('ascii')
    client_conn.send('Connected'.encode())
    ops = client_conn.recv(2048).decode('ascii')
    print(ops)

    ##send
    if ops == 'SEND':
        msg = (client_conn.recv(2048).decode('ascii'))
        request = msg.split('@')
        ADD_request_(request)

    ##remove    
    elif ops == 'REMOVE':
        msg = (client_conn.recv(2048).decode('ascii'))
        request = msg.split('@')
        REMOVE_request_(request)


    ##update
    elif ops == 'UPDATE':
        msg = (client_conn.recv(2048).decode('ascii'))
        request = msg.split('@')
        UPDATE_request_(request)

    ##fetch
    elif ops == 'FETCH':
        msg = (client_conn.recv(2048).decode('ascii'))
        request = msg.split('@')
        FETCH_request(request)

    ##get_info
    elif ops == 'GET_INFO':
        GET_request_()

    client_conn.close()
    break
