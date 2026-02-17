#ifndef BLOB_H
#define BLOB_H

#include <string>

class Blob {
public:
    const std::string hash;

    Blob(const std::string& hash) : hash(hash) {}
    Blob(std::string&& hash) : hash(std::move(hash)) {}
};

#endif //BLOB_H
