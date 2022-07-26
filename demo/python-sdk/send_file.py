import Open_LISA_SDK


def main():
    sdk = Open_LISA_SDK.SDK(log_level="DEBUG")
    sdk.connect_through_TCP("localhost", 8080)

    sdk.send_file("./image_input.bmp", "image_input.bmp")
    sdk.send_file("./processing_example.m", "processing_example.m")

    sdk.disconnect()


if __name__ == "__main__":
    main()
