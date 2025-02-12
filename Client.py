import logging
import grpc
import grpc._channel
import Service_pb2
import Service_pb2_grpc


class Service:
    def __init__(self, channel):
        self.__stub = Service_pb2_grpc.Cloud_Client(
            channel=grpc.insecure_channel(channel)
        )

    def menu(self):
        while True:
            print(
                """
                1. Create Key\n
                2. Show Key\n
                3. Update Key\n
                4. Delete Key
                """
            )
            try:
                choice = int(input("Lựa chọn : "))
            except ValueError:
                print("Lựa chọn không hợp lệ!")
                continue
            match choice:
                case 1:
                    print(self.__create())
                case 2:
                    print(self.__show())
                case 3:
                    print(self.__update())
                case 4:
                    print(self.__delete())
                case _:
                    print("Lựa chọn không hợp lệ!")

    def __create(self):
        key = input("Nhập key: ")
        value = input("Nhập value: ")
        return self.__stub.Create(Service_pb2.Record(key=key, value=value))

    def __show(self):
        key = input("Nhập key: ")
        return self.__stub.Show(Service_pb2.Key(key=key))

    def __update(self):
        key = input("Nhập key: ")
        value = input("Enter value: ")
        return self.__stub.Update(Service_pb2.Record(key=key, value=value))

    def __delete(self):
        key = input("Nhập key: ")
        return self.__stub.Delete(Service_pb2.Key(key=key))


if __name__ == "__main__":
    logging.basicConfig()
    port = input("Port: ")
    try:
        service = Service(f"localhost:{port}")
        service.menu()
    except grpc._channel._InactiveRpcError:
        print("Lỗi kết nối!")
