import Open_LISA_SDK

MATLAB_SCRIPT = "'C:\\Users\\FIUBA\\PycharmProjects\\Open-LISA-Server\\processing_example.m'"
MATLAB_COMMAND = "matlab -nodisplay -nosplash -nodesktop -r \"run {}; exit;\"".format(MATLAB_SCRIPT)


def main():
    sdk = Open_LISA_SDK.SDK(log_level="DEBUG")
    sdk.connect_through_TCP("localhost", 8080)

    return_code, stdout, stderr = sdk.execute_bash_command(MATLAB_COMMAND, True, True)

    print(return_code)
    print(stdout)
    print(stderr)

    sdk.disconnect()


if __name__ == "__main__":
    main()
