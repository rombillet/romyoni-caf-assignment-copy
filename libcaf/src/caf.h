#ifndef CAF_H
#define CAF_H

#include <unistd.h>
#include <string>
#include <cstddef>

#include "blob.h"

unsigned int hash_length();

std::string hash_file(const std::string& file_path);
std::string hash_string(const std::string& content);

Blob save_file_content(const std::string& content_root_dir, const std::string& file_path);
int open_content_for_reading(const std::string& content_root_dir, const std::string& content_hash);
int open_content_for_writing(const std::string& content_root_dir, const std::string& content_hash);

void delete_content(const std::string& content_root_dir, const std::string& content_hash);

#endif // CAF_H