import Open_LISA_SDK

# Define server config
sdk = Open_LISA_SDK.SDK(log_level="DEBUG")
sdk.connect_through_TCP("localhost", 8080)

# List instruments
print(sdk.get_instruments())
sdk.disconnect()