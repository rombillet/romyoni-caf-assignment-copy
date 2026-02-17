#ifndef HASHTYPES_H
#define HASHTYPES_H

#include <string>

#include "blob.h"
#include "tree_record.h"
#include "tree.h"
#include "commit.h"

std::string hash_object(const Blob& blob);
std::string hash_object(const Tree& tree);
std::string hash_object(const Commit& commit);

#endif // HASHTYPES_H