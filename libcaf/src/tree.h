#ifndef TREE_H
#define TREE_H

#include <map>
#include <string>
#include <utility>

#include "tree_record.h"

class Tree {
public:
    const std::map<std::string, TreeRecord> records;

    explicit Tree(const std::map<std::string, TreeRecord>& records): records(records) {}

    std::map<std::string, TreeRecord>::const_iterator record(const std::string& key) const {
        return records.find(key);
    }
};

#endif // TREE_H

