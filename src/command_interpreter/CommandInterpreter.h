#ifndef COMMAND_INTERPRETER_H
#define COMMAND_INTERPRETER_H

#include <functional>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

// Execution status enum
enum class ExecutionStatus
{
    NotExecuted,
    Executed,
    Error
};

// Structure to hold a command and its parameters
struct Command
{
    std::string         name;
    std::vector<double> parameters;
    ExecutionStatus     status = ExecutionStatus::NotExecuted;
    std::string         error;
};

// Class to interpret and execute commands
class CommandInterpreter
{
  public:
    using CommandCallback = std::function<void(Command&)>;

    void                        registerCallback(const std::string& commandName, CommandCallback callback);
    void                        executeCommands(const uint8_t* memory, size_t size);
    const std::vector<Command>& getCommands() const;

  private:
    std::unordered_map<std::string, CommandCallback> callbacks;
    std::vector<Command>                             commands;

    std::vector<Command> parseCommands(const uint8_t* memory, size_t size);
};

#endif // COMMAND_INTERPRETER_H
