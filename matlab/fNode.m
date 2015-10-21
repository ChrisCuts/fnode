
if exist('socket', 'var')
    if ~isempty(socket)
        socket.close()
    end
end
if exist('server_socket', 'var')
    if ~isempty(server_socket)
        server_socket.close()
    end
end

close all
clear *

clc

fprintf(['=========================================\n'...
         '| Welcome to MATLAB fNODES client\n'...
         '=========================================\n\n'])

addpath('jsonlab')

import java.net.Socket
import java.net.ServerSocket
import java.io.*

host = 'localhost';
port = 53715;

registration = 'Hallo fNODES. Here is MATLAB.';


fprintf('Try to connect to fNODES host application.. ')

socket = [];

line = '';

try
    socket = java.net.Socket(host, port);

    fprintf('\t done.\n')
    writer = PrintWriter( OutputStreamWriter ( socket.getOutputStream ));

    writer.print(registration);
    writer.flush();

    reader = BufferedReader( InputStreamReader ( socket.getInputStream ));

    while 1
        chr = reader.read();
        if chr == -1
            break
        end
        line = [line chr];
    end
    
    
catch ME
    if ~isempty(socket)
        socket.close()
    end
    
    fprintf('\n\nCannot connect to host.\n\n')
    rethrow(ME)
    
end
    
if strcmpi(line, 'Welcome MATLAB')
   
    fprintf('Connection granted.\n\n')
    
else

    fprintf('connection refused.\n\n')
    return
end



fprintf('Waiting for instructions..\n\n')

server_socket = [];
socket = [];

variable_space = {};

disp('create socket')
        
while 1
    
    try
        
        server_socket = ServerSocket(port+1);
        server_socket.setSoTimeout(5000);
        
        socket = server_socket.accept();
        
        reader = BufferedReader( InputStreamReader ( socket.getInputStream ));
        
        line = reader.readLine();
           
        %line = StringEscapeUtils.escapeJava(line);
        
        line = loadjson(char(line));
        
        if strcmp(line, 'QUIT_SESSION')
            disp('Quit session')
        
            writer = PrintWriter( OutputStreamWriter ( socket.getOutputStream ));

            out = savejson('', {'DONE'});
            writer.print(out);
            writer.flush();

            server_socket.close();
            socket.close();

            break
        end
        
        [out, variable_space] = execute(line, variable_space);
        
        out = savejson('', out);
        
        writer = PrintWriter( OutputStreamWriter ( socket.getOutputStream ));

        writer.print(out);
        writer.flush();

        server_socket.close();
        socket.close();
        
    catch ME
        if ~isempty(server_socket)
            server_socket.close();
        end
        if ~isempty(socket)
            socket.close();
        end
        
        if any(strcmpi(properties(ME), 'ExceptionObject')) && strcmpi(class(ME.ExceptionObject), 'java.net.SocketTimeoutException')
             continue
        else
            rethrow(ME)
        end
    end
    
end


