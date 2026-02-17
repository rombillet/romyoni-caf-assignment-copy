from libcaf import Tree, TreeRecord, TreeRecordType


def test_tree_entries_are_canonicalized() -> None:
    """Test that tree entries are canonicalized (sorted) regardless of insertion order."""
    # Create tree records
    record_a = TreeRecord(TreeRecordType.BLOB, '1111111111111111111111111111111111111111', 'a_file')
    record_b = TreeRecord(TreeRecordType.BLOB, '2222222222222222222222222222222222222222', 'b_file')
    record_c = TreeRecord(TreeRecordType.BLOB, '3333333333333333333333333333333333333333', 'c_file')

    # Create trees with entries in different orders
    # Third tree with deliberately non-alphabetical order
    tree1 = Tree({'a_file': record_a, 'b_file': record_b, 'c_file': record_c})
    tree2 = Tree({'c_file': record_c, 'a_file': record_a, 'b_file': record_b})
    tree3 = Tree({'b_file': record_b, 'c_file': record_c, 'a_file': record_a})

    # Extract keys from each tree and print them for debugging
    tree1_keys = list(tree1.records.keys())
    tree2_keys = list(tree2.records.keys())
    tree3_keys = list(tree3.records.keys())

    print('Tree 1 keys:', tree1_keys)
    print('Tree 2 keys:', tree2_keys)
    print('Tree 3 keys:', tree3_keys)

    # The keys should be sorted alphabetically regardless of insertion order
    expected_keys = ['a_file', 'b_file', 'c_file']

    # This test should fail currently because Tree doesn't canonicalize entries
    assert tree1_keys == tree2_keys == tree3_keys == expected_keys, 'Tree entries are not properly canonicalized'
