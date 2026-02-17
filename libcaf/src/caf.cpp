#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/file.h>
#include <openssl/evp.h>
#include <tuple>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <memory>
#include <iomanip>
#include <sstream>
#include <vector>
#include <chrono>
#include <thread>

#include "caf.h"

constexpr size_t BUFFER_SIZE = 4096;
constexpr size_t DIR_NAME_SIZE = 2;

std::string create_sub_dir(const std::string& content_root_dir, const std::string& hash);
void lock_file_with_timeout(int fd, int operation, int timeout_sec);
void copy_file(const std::string& src, const std::string& dest);
void create_content_path(const std::string& content_root_dir, const std::string& hash, std::string& output_path);

std::string hash_file(const std::string& filename) {
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx){
        throw std::runtime_error("Failed to create EVP_MD_CTX");
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), nullptr) != 1){
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to initialize digest");
    }

    std::ifstream file(filename, std::ios::binary);
    if (!file){
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to open file");
    }

    std::vector<char> buffer(BUFFER_SIZE);
    while (file.read(buffer.data(), BUFFER_SIZE)) {
        if (EVP_DigestUpdate(mdctx, buffer.data(), BUFFER_SIZE) != 1){
            EVP_MD_CTX_free(mdctx);
            throw std::runtime_error("Failed to update digest");
        }
    }

    // Handle the last partial read
    if (file.gcount() > 0) {
        if (EVP_DigestUpdate(mdctx, buffer.data(), file.gcount()) != 1){
            EVP_MD_CTX_free(mdctx);
            throw std::runtime_error("Failed to update digest");
        }
    }

    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1){
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to finalize digest");
    }

    EVP_MD_CTX_free(mdctx);

    std::ostringstream oss;
    oss << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < hash_len; ++i) {
        oss << std::setw(2) << static_cast<unsigned int>(hash[i]);
    }

    return oss.str();
}

std::string hash_string(const std::string& content) {
    EVP_MD_CTX* mdctx = EVP_MD_CTX_new();
    if (mdctx == nullptr) {
        throw std::runtime_error("Failed to create EVP_MD_CTX");
    }

    const EVP_MD* md = EVP_sha1();
    if (EVP_DigestInit_ex(mdctx, md, nullptr) != 1) {
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to initialize digest");
    }

    if (EVP_DigestUpdate(mdctx, content.c_str(), content.size()) != 1) {
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to update digest");
    }

    // Get the actual hash size from OpenSSL
    int hash_size = EVP_MD_size(md);
    std::vector<unsigned char> hash(hash_size);
    unsigned int hash_len;

    if (EVP_DigestFinal_ex(mdctx, hash.data(), &hash_len) != 1) {
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to finalize digest");
    }

    EVP_MD_CTX_free(mdctx);

    std::ostringstream oss;
    oss << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < hash_len; ++i) {
        oss << std::setw(2) << static_cast<unsigned int>(hash[i]);
    }

    return oss.str();
}

unsigned int hash_length() {
    return EVP_MD_size(EVP_sha1()) * 2;
}

Blob save_file_content(const std::string& content_root_dir, const std::string& file_path) {
    std::error_code ec;
    std::filesystem::create_directories(content_root_dir, ec);
    if (ec && ec != std::errc::file_exists) {
        throw std::runtime_error("Failed to create root directory: " + ec.message());
    }

    // Set directory permissions to 0755 (owner: rwx, group/others: rx)
    std::filesystem::permissions(content_root_dir,
        std::filesystem::perms::owner_all | std::filesystem::perms::group_read |
        std::filesystem::perms::others_read, ec);

    std::string file_hash = hash_file(file_path);

    std::string content_path;
    create_content_path(content_root_dir, file_hash, content_path);

    int fd = open(content_path.c_str(), O_WRONLY | O_CREAT, 0644);

    if (fd < 0)
        throw std::runtime_error("Failed to open file");

    try{
        lock_file_with_timeout(fd, LOCK_EX, 10);
    } catch (const std::exception& e){
        close(fd);
        throw;
    }

    try {
        copy_file(file_path, content_path);
    } catch (const std::exception& e) {
        std::error_code ec;
        std::filesystem::remove(content_path, ec);
        flock(fd, LOCK_UN);
        close(fd);
        throw;
    }

    flock(fd, LOCK_UN);
    close(fd);

    return Blob(file_hash);
}

int open_content_for_writing(const std::string& content_root_dir, const std::string& content_hash) {
    std::error_code ec;
    std::filesystem::create_directories(content_root_dir, ec);
    if (ec && ec != std::errc::file_exists) {
        throw std::runtime_error("Failed to create root directory: " + ec.message());
    }

    // Set directory permissions to 0755 (owner: rwx, group/others: rx)
    std::filesystem::permissions(content_root_dir,
        std::filesystem::perms::owner_all |
        std::filesystem::perms::group_read | std::filesystem::perms::group_exec |
        std::filesystem::perms::others_read | std::filesystem::perms::others_exec, ec);

    std::string content_path;
    create_content_path(content_root_dir, content_hash, content_path);

    int fd = open(content_path.c_str(), O_WRONLY|O_CREAT, 0644);

    if (fd < 0) {
        throw std::runtime_error("Failed to open file");
    }

    try{
        lock_file_with_timeout(fd, LOCK_EX, 10);
    } catch (const std::exception& e){
        close(fd);
        throw;
    }

    return fd;
}

void delete_content(const std::string& content_root_dir, const std::string& content_hash) {
    std::string content_path;
    create_content_path(content_root_dir, content_hash, content_path);

    int fd = open(content_path.c_str(), O_RDONLY);
    if (fd < 0)
    {
        if (errno == ENOENT)
            return;
        throw std::runtime_error("Failed to open file");
    }

    try{
            lock_file_with_timeout(fd, LOCK_EX, 10);
        } catch (const std::exception& e){
            close(fd);
            throw;
        }

    std::error_code ec;
    if (!std::filesystem::remove(content_path, ec)) {
        flock(fd, LOCK_UN);
        close(fd);
        throw std::runtime_error("Failed to delete file: " + ec.message());
    }

    flock(fd, LOCK_UN);
    close(fd);
}

int open_content_for_reading(const std::string& content_root_dir, const std::string& content_hash) {
    std::string content_path;
    create_content_path(content_root_dir, content_hash, content_path);

    int fd = open(content_path.c_str(), O_RDONLY);

    if (fd < 0)
        throw std::runtime_error("Failed to open file");

    try{
        lock_file_with_timeout(fd, LOCK_EX, 10);
    } catch (const std::exception& e){
        close(fd);
        throw;
    }

    return fd;
}

void copy_file(const std::string& src, const std::string& dest) {
    std::ifstream source_file(src, std::ios::binary);
    if (!source_file) {
        throw std::runtime_error("Failed to open source file");
    }

    std::ofstream dest_file(dest, std::ios::binary);
    if (!dest_file) {
        throw std::runtime_error("Failed to open destination file");
    }

    std::vector<char> buffer(BUFFER_SIZE);
    while (source_file.read(buffer.data(), BUFFER_SIZE)) {
        if (!dest_file.write(buffer.data(), BUFFER_SIZE)) {
            throw std::runtime_error("Failed to write to destination file");
        }

        if (dest_file.fail()) {
            throw std::runtime_error("Error while writing to destination file");
        }
    }

    // Handle the last partial read
    if (source_file.gcount() > 0) {
        if (!dest_file.write(buffer.data(), source_file.gcount())) {
            throw std::runtime_error("Failed to write to destination file");
        }

        if (dest_file.fail()) {
            throw std::runtime_error("Error while writing to destination file");
        }
    }

    // Explicit flush to ensure all data is written
    dest_file.flush();
    if (dest_file.fail()) {
        throw std::runtime_error("Failed to flush destination file");
    }
}

void create_content_path(const std::string& content_root_dir, const std::string& hash, std::string& output_path) {
    if (content_root_dir.empty() || hash.empty())
        throw std::invalid_argument("Invalid argument");

    output_path = create_sub_dir(content_root_dir, hash) + "/" + hash;
}

std::string create_sub_dir(const std::string& content_root_dir, const std::string& hash) {
    if (content_root_dir.empty() || hash.length() < 2)
        throw std::invalid_argument("Invalid argument");

    std::string sub_dir_path = content_root_dir + "/" + hash.substr(0, 2);

    std::error_code ec;
    std::filesystem::create_directories(sub_dir_path, ec);
    if (ec && ec != std::errc::file_exists) {
        throw std::runtime_error("Failed to create sub directory: " + ec.message());
    }

    // Set directory permissions to 0755 (owner: rwx, group/others: rx)
    std::filesystem::permissions(sub_dir_path,
        std::filesystem::perms::owner_all |
        std::filesystem::perms::group_read | std::filesystem::perms::group_exec |
        std::filesystem::perms::others_read | std::filesystem::perms::others_exec, ec);

    return sub_dir_path;
}

void lock_file_with_timeout(int fd, int operation, int timeout_sec){
    auto start_time = std::chrono::steady_clock::now();
    auto timeout_duration = std::chrono::seconds(timeout_sec);

    while (flock(fd, operation | LOCK_NB) != 0) {
        if (errno == EWOULDBLOCK) {
            auto elapsed = std::chrono::steady_clock::now() - start_time;
            if (elapsed >= timeout_duration)
                throw std::runtime_error("Failed to acquire lock");
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        else
            throw std::runtime_error("Failed to acquire lock");
    }
}
