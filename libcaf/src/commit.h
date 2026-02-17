#ifndef COMMIT_H
#define COMMIT_H

#include <string>
#include <ctime>
#include <optional>

class Commit {
public:
    const std::string tree_hash;  // Hash of the tree object
    const std::string author;     // Author of the commit
    const std::string message;    // Commit message
    const std::time_t timestamp;  // Timestamp of the commit
    const std::optional<std::string> parent; // Parent commit hash

    Commit(const std::string& tree_hash, const std::string& author, const std::string& message, std::time_t timestamp, std::optional<std::string> parent = std::nullopt):
            tree_hash(tree_hash), author(author), message(message), timestamp(timestamp), parent(parent) {}
};

#endif // COMMIT_H
