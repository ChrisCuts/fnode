function [out, variable_space] = execute(message, variable_space)

% default output
out = {'ERROR', 'MATLAB doesn''t know what to do with this message.'};

if ~iscell(message) || length(message) < 1 || length(message) > 2
    disp(message)
    out = {'ERROR', 'Message must be an opcode or a pair with opcode and command.'};
    return
end

if ~ischar(message{1})
    
    out = {'ERROR', 'Opcode must be a string.'};
    return
end



funs.EDIT_CODE = @edit_code;
funs.ADD_PATH = @add_path;
funs.REMOVE_PATH = @remove_path;
funs.CLEAR = @clear_space;
funs.CALL_M_FUNCTION = @(command)call_function(command, variable_space);


if strcmp(message{1}, 'CALL_M_FUNCTION')
    
    [out, variable_space] = funs.(message{1})(message{2});

elseif isfield(funs, message{1})
    
    
    out = funs.(message{1})(message{2:end});
else
    
    out = {'ERROR', ['Unknown opcode: ' message{1}]};
end


end



function out = edit_code(command)

if exist(command, 'file')
    edit(command)
    out = {'DONE'};
    
else
    out = {'ERROR', ['File not found: ' command ]};
    
end

end

function out = add_path(command)

if iscellstr(command)
    addpath(command{:})
    out = {'DONE'};
elseif ischar(command)
    addpath(command)
    out = {'DONE'};
else
    out = {'ERROR', ['Wrong command type: ' class(command) '. Must be a cellstring or string.']};
end

end

function out = remove_path(command)

if iscellstr(command)
    rmpath(command{:})
    out = {'DONE'};
elseif ischar(command)
    rmpath(command)
    out = {'DONE'};
else
    out = {'ERROR', ['Wrong command type: ' class(command) '. Must be a cellstring or string.']};
end

end

function out = clear_space()

disp('clear')
% clear *
% close all

out = {'DONE'};

end

function [out, variable_space] = call_function(command, variable_space)



if strcmpi(command.name(end-1:end), '.m')
    
    
    fun = str2func(command.name(1:end-2));
    
    
    
    %%% prepare call variables
    if isfield(command, 'fields')
        if isfield(command.fields, 'inputs')
            inputs = struct2cell(command.fields.inputs);
            
            %%% replace integer values with variable_space indices
            indices = cell2mat(inputs(cellfun(@(x)~isempty(x), inputs)));
            inputs(cellfun(@(x)~isempty(x), inputs)) = variable_space(indices);
        else
            inputs = [];
            
        end
        if isfield(command.fields, 'outputs')
            outputs = cell(length(fieldnames(command.fields.outputs)), 1);
        else
            outputs = [];
        end
        if isfield(command.fields, 'options')
            options = command.fields.options;
            
            for name = fieldnames(options)
                
                if iscell(options.(char(name)))
                    options.(char(name)) = options.(char(name)){2};
                elseif isscalar(options.(char(name)))
                    options.(char(name)) = variable_space{options.(char(name))};
                end
            end
            
        else
            options = [];
        end
    else
        inputs = [];
        outputs = [];
        options = [];
        
    end
    
    %TODO: try catch
    if isempty(inputs) && isempty(options)
        [outputs{:}] = fun();
    else
        in = [inputs, options];
        [outputs{:}] = fun(in{:});
    end
    
    
    %%% handle outputs
    if ~isempty(outputs)
        out = struct2cell(command.fields.outputs);
            
        %%% replace integer values with variable_space indices
        indices = cell2mat(out(cellfun(@(x)~isempty(x), out)));
        variable_space(indices) = outputs(cellfun(@(x)~isempty(x), out));
        
        outputs = outputs(cellfun(@(x)isempty(x), out));
        
        
        if isempty(outputs)
            out = {'DONE'};
        else
            out = {'RETURN', outputs};
        end
    end
       
    
else
    out = {'ERROR', ['Wrong file type: ' command.name(end-2:end)]};
end

end