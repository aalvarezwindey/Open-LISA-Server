import Open_LISA_SDK


def main():
    sdk = Open_LISA_SDK.SDK(log_level="DEBUG")
    sdk.connect_through_TCP("localhost", 8080)

    sdk.get_file("image_output.bmp", "image_local_from_remote.bmp")

    sdk.disconnect()


if __name__ == "__main__":
    main()
