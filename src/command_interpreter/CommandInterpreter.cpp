#include "CommandInterpreter.h"

void CommandInterpreter::registerCallback(const std::string& commandName, CommandCallback callback)
{
    callbacks[commandName] = callback;
}

void CommandInterpreter::executeCommands(const uint8_t* memory, size_t size)
{
    commands = parseCommands(memory, size);
    for (auto& command : commands)
    {
        if (callbacks.find(command.name) != callbacks.end())
        {
            try
            {
                callbacks[command.name](command);
                command.status = ExecutionStatus::Executed;
            }
            catch (const std::exception& e)
            {
                command.status = ExecutionStatus::Error;
                command.error  = e.what();
            }
        }
        else
        {
            command.status = ExecutionStatus::Error;
            command.error  = "No callback registered for command: " + command.name;
        }
    }
}

std::vector<Command> CommandInterpreter::parseCommands(const uint8_t* memory, size_t size)
{
    std::vector<Command> parsedCommands;
    std::istringstream   stream(std::string(reinterpret_cast<const char*>(memory), size));
    std::string          line;

    while (std::getline(stream, line))
    {
        std::istringstream lineStream(line);
        Command            command;
        lineStream >> command.name;

        double param;
        while (lineStream >> param)
        {
            command.parameters.push_back(param);
        }

        parsedCommands.push_back(command);
    }

    return parsedCommands;
}

const std::vector<Command>& CommandInterpreter::getCommands() const { return commands; }
