#include "hash_types.h"
#include "caf.h"

std::string hash_object(const Blob& blob) {
    return blob.hash;
}

std::string hash_object(const Tree& tree) {
    std::string acc_std;

    for (const auto& [key, record] : tree.records) {
        acc_std += record.name + std::to_string(static_cast<int>(record.type)) + record.hash;
    }

    return hash_string(acc_std);
}

std::string hash_object(const Commit& commit) {
    return hash_string(commit.tree_hash + commit.author + commit.message +
                       std::to_string(commit.timestamp) + commit.parent.value_or(""));
}