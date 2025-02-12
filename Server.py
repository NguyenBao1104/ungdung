import grpc
import Service_pb2
import Service_pb2_grpc
from concurrent import futures
import logging
from Nodes import NODES
from tabulate import tabulate

CLOUD = {}


server_port = input("Nhập Port: ")


class Cloud(Service_pb2_grpc.CloudServicer):
    def __init__(self):
        self.__neibor_stubs = [
            Service_pb2_grpc.Cloud_Client(
                channel=grpc.insecure_channel(f"localhost:{port}")
            )
            for port in NODES
            if port != server_port
        ]

    def Create(self, request, context):
        if request.key in CLOUD.keys():
            return Service_pb2.Response(
                status_code=404, message=f"Key {request.key} đã tồn tại!"
            )
        CLOUD[request.key] = request.value
        self.__create_sync(request.key, request.value)
        self.__show()
        return Service_pb2.Response(
            status_code=200,
            message=f"Cặp Key-Value {{{request.key}: {request.value}}} đã được thêm!",
        )

    def Show(self, request, context):
        if request.key not in CLOUD.keys():
            return Service_pb2.Response(status_code=404, message="Không tìm thấy Key!")
        return Service_pb2.Response(
            status_code=200, message=f"{{{request.key}: {CLOUD.get(request.key)}}}"
        )

    def Update(self, request, context):
        if request.key not in CLOUD.keys():
            return Service_pb2.Response(status_code=404, message="Không tìm thấy Key!")
        if CLOUD[request.key] != request.value:
            CLOUD[request.key] = request.value
            self.__update_sync(request.key, request.value)
            self.__show()
        return Service_pb2.Response(
            status_code=200,
            message=f"Cặp Key-Value {{{request.key}: {request.value}}} đã được cập nhật!",
        )

    def Delete(self, request, context):
        if request.key not in CLOUD.keys():
            return Service_pb2.Response(status_code=404, message="Không tìm thấy Key!")
        CLOUD.pop(request.key)
        self.__delete_sync(request.key)
        self.__show()
        return Service_pb2.Response(
            status_code=200, message=f"Key {request.key} đã được xóa!"
        )

    def __create_sync(self, key, value):
        for stub in self.__neibor_stubs:
            stub.Create(Service_pb2.Record(key=key, value=value))

    def __update_sync(self, key, value):
        for stub in self.__neibor_stubs:
            stub.Update(Service_pb2.Record(key=key, value=value))

    def __delete_sync(self, key):
        for stub in self.__neibor_stubs:
            stub.Delete(Service_pb2.Key(key=key))

    def __show(self):
        datas = [(k, v) for k, v in CLOUD.items()]
        print(tabulate(datas, headers=["key", "value"], tablefmt="grid"))


def server():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Service_pb2_grpc.add_CloudServicer_to_server(
        Cloud(), server=server
    )
    server.add_insecure_port(f"[::]:{server_port}")
    server.start()
    print(f"Đang hoạt động trên Port: {server_port}")
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    server()
