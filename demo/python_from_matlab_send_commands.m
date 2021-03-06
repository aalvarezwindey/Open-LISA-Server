pcPythonExe = 'C:\Users\gabro\AppData\Local\Programs\Python\Python39\python.exe';
%[ver, exec, loaded]	= pyversion(pcPythonExe);
pyversion

py.print("Conexión con el servidor")
server_ip = "192.168.1.109"
server_port = 8080
eia_sdk = py.electronic_instrument_adapter_sdk.EIA(server_ip, server_port)

try
    py.print("************ Lista de Instrumentos: ************ ")
    instruments = eia_sdk.list_instruments()

    % El ID del oscilloscopío es: USB0::0x0699::0x0363::C107676::INSTR
    
    py.print("************ Ver deatlle de Instrumento: ************ ")
    osciliscopio = eia_sdk.get_instrument("USB0::0x0699::0x0363::C107676::INSTR")

    py.print("************ Ver comandos disponibles para Instrumento: ************ ")
    osciliscopio.available_commands()
    
    py.print("*********** Set channel 1 volts scale to 5.0V ************");
    osciliscopio.send("set_channel_volts_scale_ch1 2.0")

catch e
    fprintf(1,'The identifier was:\n%s',e.identifier);
    fprintf(1,'There was an error! The message was:\n%s',e.message);
    eia_sdk.disconnect()
end

eia_sdk.disconnect()