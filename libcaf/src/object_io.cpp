#include <string>
#include <unistd.h>
#include <fcntl.h>
#include <sys/file.h>
#include <vector>
#include <cstring>
#include <stdexcept>
#include <map>

#include "caf.h"
#include "object_io.h"
#include "hash_types.h"

// Maximum string length for length-prefixed strings
constexpr uint32_t MAX_LENGTH = 1024 * 1024;  // 1 MB limit for strings

std::string read_length_prefixed_string(int fd); // Helper function to read a length-prefixed string safely
void write_with_length(int fd, const std::string &data); // Helper function to write a length-prefixed string safely
void save_tree_record(int fd, const TreeRecord &record); // Helper function to serialize a TreeRecord
TreeRecord load_tree_record(int fd); // Helper function to deserialize a TreeRecord

// Serialize Commit to disk
void save_commit(const std::string &root_dir, const Commit &commit) {
    std::string commit_hash = hash_object(commit);

    int fd = open_content_for_writing(root_dir, commit_hash);

    try {
        write_with_length(fd, commit.tree_hash);
        write_with_length(fd, commit.author);
        write_with_length(fd, commit.message);

        if (write(fd, &commit.timestamp, sizeof(commit.timestamp)) != sizeof(commit.timestamp))
            throw std::runtime_error("Failed to write timestamp");

        if (commit.parent) {
            write_with_length(fd, *commit.parent);
        } else {
            uint32_t length = 0;
            if (write(fd, &length, sizeof(length)) != sizeof(length))
                throw std::runtime_error("Failed to write parent");
        }

        flock(fd, LOCK_UN);
        close(fd);
    } catch (const std::exception &e) {
        delete_content(root_dir, commit_hash);
        throw;
    }
}

// Deserialize Commit from disk
Commit load_commit(const std::string &root_dir, const std::string &commit_hash) {
    int fd = open_content_for_reading(root_dir, commit_hash);

    std::string tree_hash = read_length_prefixed_string(fd);
    std::string author = read_length_prefixed_string(fd);
    std::string message = read_length_prefixed_string(fd);

    uint64_t timestamp;
    if (read(fd, &timestamp, sizeof(timestamp)) != sizeof(timestamp))
        throw std::runtime_error("Failed to read timestamp");

    std::string parent_str = read_length_prefixed_string(fd);

    flock(fd, LOCK_UN);
    close(fd);

    std::optional<std::string> parent = parent_str.empty() ? std::nullopt : std::make_optional(parent_str);
    return Commit(tree_hash, author, message, timestamp, parent);
}

void save_tree(const std::string &root_dir, const Tree &tree) {
    std::string tree_hash = hash_object(tree);

    int fd = open_content_for_writing(root_dir, tree_hash);

     try {
        uint32_t num_records = tree.records.size();
        if (write(fd, &num_records, sizeof(num_records)) != sizeof(num_records))
            throw std::runtime_error("Failed to write number of records");

        for (const auto &[name, record] : tree.records) {
            save_tree_record(fd, record);
        }

        flock(fd, LOCK_UN);
        close(fd);
    } catch (const std::exception &e) {
        delete_content(root_dir, tree_hash);
        throw;
    }
}

Tree load_tree(const std::string &root_dir, const std::string &tree_hash) {
    int fd = open_content_for_reading(root_dir.c_str(), tree_hash.c_str());

    uint32_t num_records;
    if (read(fd, &num_records, sizeof(num_records)) != sizeof(num_records))
        throw std::runtime_error("Failed to read the number of records");

    std::map<std::string, TreeRecord> records;
    for (uint32_t i = 0; i < num_records; ++i) {
        TreeRecord record = load_tree_record(fd);
        records.emplace(record.name, record);
    }

    flock(fd, LOCK_UN);
    close(fd);

    return Tree(records);
}

std::string read_length_prefixed_string(int fd) {
    uint32_t length;
    if (read(fd, &length, sizeof(length)) != sizeof(length))
        throw std::runtime_error("Failed to read length");

    if (length > MAX_LENGTH)
        throw std::runtime_error("Length exceeds maximum");

    std::string result(length, '\0');

    if (read(fd, &result[0], length) != static_cast<ssize_t>(length))
        throw std::runtime_error("Failed to read string");

    return result;
}

void write_with_length(int fd, const std::string &data) {
    uint32_t length = data.length();
    if (write(fd, &length, sizeof(length)) != sizeof(length) || write(fd, data.c_str(), length) != static_cast<ssize_t>(length)) {
        throw std::runtime_error("Failed to write string");
    }
}

void save_tree_record(int fd, const TreeRecord &record) {
    uint8_t type = static_cast<uint8_t>(record.type);
    if (write(fd, &type, sizeof(type)) != sizeof(type))
        throw std::runtime_error("Failed to write type");

    write_with_length(fd, record.hash);
    write_with_length(fd, record.name);
}

TreeRecord load_tree_record(int fd) {
    uint8_t type;

    if (read(fd, &type, sizeof(type)) != sizeof(type)) {
        throw std::runtime_error("Failed to read TreeRecord type");
    }

    TreeRecord::Type record_type = static_cast<TreeRecord::Type>(type);
    std::string hash = read_length_prefixed_string(fd);
    std::string name = read_length_prefixed_string(fd);

    return TreeRecord(record_type, hash, name);
}