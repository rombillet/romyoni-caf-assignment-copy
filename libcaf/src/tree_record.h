#ifndef TREERECORD_H
#define TREERECORD_H

#include <string>

class TreeRecord {
public:
    enum class Type {
        TREE,
        BLOB,
        COMMIT
    };
    
    const Type type;
    const std::string hash;
    const std::string name;

    TreeRecord(Type type, std::string hash, std::string name)
        : type(type), hash(hash), name(name) {}
};

#endif // TREERECORD_H
