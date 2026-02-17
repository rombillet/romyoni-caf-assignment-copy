#ifndef OBJECT_IO_H
#define OBJECT_IO_H

#include <string>
#include <utility>
#include <vector>
#include <stdexcept>
#include <cstdint>

#include "commit.h"
#include "tree.h"

void save_commit(const std::string &root_dir, const Commit &commit);
Commit load_commit(const std::string &root_dir, const std::string &hash);
void save_tree(const std::string &root_dir, const Tree &tree);
Tree load_tree(const std::string &root_dir, const std::string &hash);


#endif // OBJECT_IO_H
