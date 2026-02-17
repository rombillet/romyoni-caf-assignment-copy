# CAF - Content Addressable Filesystem

<div align="center">
  <img src="assignment/assets/asp-title.png" alt="Advanced Systems Programming - CAF Project" width="600">
</div>

A lightweight version control system similar to Git, written in Python and C++.
CAF serves as an educational project for understanding how complex distributed version control systems work under the
hood.

[![Test CI](https://github.com/idoby/asp-caf-assignment/actions/workflows/tests.yml/badge.svg)](https://github.com/idoby/asp-caf-assignment/actions/workflows/tests.yml)

## 🌟 Project Overview

CAF (Content Addressable Filesystem) is a simplified version control system that implements core Git-like functionality
including:

- Repository initialization and management
- File content hashing and storage
- Commit creation and tracking
- Branch management
- File system operations with content-addressable storage

The project demonstrates the fundamental concepts behind modern version control systems, including content-addressable
storage, object models, and distributed workflows.

## 🏗️ Architecture

CAF is built as a hybrid Python/C++ system:

- **Python Layer**: Command-line interface, high-level repository operations, and user-facing functionality
- **C++ Core**: High-performance hashing, object storage, and low-level file operations
- **Integration**: Python bindings using pybind11 for seamless interoperability

### Key Components

- **`caf/`**: Python CLI application and command implementations
- **`libcaf/`**: Core C++ library with Python bindings
- **`tests/`**: Comprehensive test suite for both Python and C++ components

## 🚀 Quick Start

### Prerequisites

- Docker (recommended for consistent environment)
- Python 3.10+
- CMake 3.15+ and C++17 compiler

### Using Docker (Recommended)

1. **Build and run the development container:**
   ```bash
   make run
   ```

2. **Attach to the container:**
   ```bash
   make attach
   ```

3. **Deploy the project inside the container:**
   ```bash
   make deploy
   ```

4. **Run tests to verify setup:**
   ```bash
   make test
   ```
   or
   ```bash
   pytest
   ```

## 💻 Usage

### Basic Commands

Initialize a new repository:

```bash
caf init
```

Create a commit:

```bash
caf commit --author "Your Name" --message "Initial commit"
```

Hash a file and optionally store it:

```bash
caf hash_file path/to/file.txt --write
```

Manage branches:

```bash
caf add_branch feature-branch
caf delete_branch old-branch
caf branch                    # List all branches
caf branch_exists my-branch   # Check if a branch exists
```

View repository history and changes:

```bash
caf log                       # Show commit log
caf diff commit1 commit2      # Compare two commits
```

Repository management:

```bash
caf delete_repo              # Delete the repository
```

Get help:

```bash
caf --help
caf <command> --help
```

## 🧪 Testing

The project includes comprehensive tests for both Python and C++ components:

- **Run all tests:** `make test`
- **Test with coverage:** `make test ENABLE_COVERAGE=1`(C++ coverage available only if compiled with coverage)

## 📁 Project Structure

```
asp-caf-assignment/
├── Dockerfile                # Development environment setup
├── Makefile                  # Build and development commands
├── assignment/               # Assignment source
├── caf/                      # Python CLI application
│   ├── pyproject.toml        # Python package configuration
│   └── caf/                  # CLI source code
│       ├── __main__.py       # Entry point
│       ├── cli.py            # Command-line interface
│       └── cli_commands.py   # Command implementations
├── libcaf/                   # Core C++ library
│   ├── CMakeLists.txt        # CMake build configuration
│   ├── pyproject.toml        # Python package configuration
│   ├── libcaf/               # Python interface and higher-level repo operations
│   │   ├── constants.py      # Constants and configuration
│   │   ├── plumbing.py       # Low-level repo operations
│   │   ├── ref.py            # Reference handling
│   │   └── repository.py     # Repository management and high-level API
│   └── src/                  # C++ source code
│       ├── bind.cpp          # Python bindings
│       ├── blob.h            # Blob object definitions
│       ├── caf.cpp/h         # Low-level C++ implementation
│       ├── commit.h          # Commit object definitions
│       ├── hash_types.cpp/h  # Hashing implementations
│       ├── object_io.cpp/h   # Object I/O operations
│       ├── tree.h            # Tree object definitions
│       └── tree_record.h     # Tree record structures
└── tests/                    # Test suite
    ├── caf/                  # CLI tests
    └── libcaf/               # Core library tests
```

## 🔧 Development

### Available Make Targets

- `make build-container` - Build Docker development image
- `make run` - Start development container
- `make attach` - Connect to running container
- `make stop` - Stop running container
- `make deploy/deploy-libcaf/deploy-caf` - Install libcaf and caf packages, or both
- `make test` - Run complete test suite (use `ENABLE_COVERAGE=1` to collect coverage information)
- `make clean` - Remove build artifacts

### Code Quality

The project follows Python and C++ best practices:

- Type hints in Python code
- Comprehensive test coverage
- Clear documentation and comments
- Consistent code formatting

## 🎓 Educational Context

This project is part of the Advanced Systems Programming course (ASP) and serves as a hands-on introduction to:

- **Systems Programming**: Working with multi-language codebases
- **Version Control Internals**: Understanding how Git-like systems work
- **Software Architecture**: Designing modular, maintainable systems
- **Testing and Debugging**: Ensuring code quality and reliability
- **Build Systems**: Managing complex build processes

Students work through various tasks including:

1. Code analysis and architecture mapping
2. Environment setup and testing
3. Debugging and fixing issues
4. Implementing new features (like tagging systems)

## 🤝 Contributors

### Initial Development

- **Meshi, Bar and Omer** - Initial design and implementation (March 2025)
- **Ido** - Refactoring, cleanup, consistency and beauty pass (June 2025)
- **You?** - Your work here! (August 2025)

## 📚 Learning Resources

To better understand the concepts behind CAF, consider exploring:

### Version Control & Systems Programming

- [Git Internals](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) - Understanding how Git stores
  and manages data
- [Content-Addressable Storage](https://en.wikipedia.org/wiki/Content-addressable_storage) - The fundamental concept
  behind Git and CAF
- [The Architecture of Open Source Applications - Git](http://aosabook.org/en/git.html) - Deep dive into Git's design
- [Git Internals - Plumbing and Porcelain (YouTube)](https://www.youtube.com/watch?v=P6jD966jzlk) - Video explanation of
  Git's internal structure
- [How Git Works Under the Hood](https://www.freecodecamp.org/news/git-internals-objects-branches-create-repo/) -
  FreeCodeCamp article on Git internals

### Python Programming

- [Python Tutorial](https://docs.python.org/3/tutorial/) - Official Python tutorial for beginners
- [Real Python](https://realpython.com/) - Practical Python tutorials and guides
- [Python C Extensions](https://docs.python.org/3/extending/) - How Python interfaces with C/C++
- [Python Type Hints](https://docs.python.org/3/library/typing.html) - Modern Python type annotations
- [Python Tutorial for Beginners (YouTube)](https://www.youtube.com/watch?v=_uQrJ0TkZlc) - 6-hour comprehensive Python
  course
- [Python Type Hints Explained (YouTube)](https://www.youtube.com/watch?v=QORvB-_mbZ0) - ArjanCodes type hints tutorial
- [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/) - Free online book for practical Python

### C++ Programming

- [LearnCpp.com](https://www.learncpp.com/) - Comprehensive C++ tutorial from basics to advanced
- [C++ Reference](https://cppreference.com/) - Complete C++ language and library reference
- [Modern C++ Features](https://github.com/AnthonyCalandra/modern-cpp-features) - C++11/14/17/20 features guide
- [C++ Tutorial for Beginners (YouTube)](https://www.youtube.com/watch?v=vLnPwxZdW4Y) - 4-hour complete C++ course
- [C++ Weekly (YouTube Channel)](https://www.youtube.com/c/lefticus1) - Short weekly C++ tips and tricks
- [Back to Basics: RAII and the Rule of Zero (YouTube)](https://www.youtube.com/watch?v=7Qgd9B1KuMQ) - CppCon talk on
  C++ best practices

### Python-C++ Integration

- [pybind11 Documentation](https://pybind11.readthedocs.io/) - Seamless operability between C++11 and Python
- [pybind11 Tutorial](https://pybind11.readthedocs.io/en/stable/basics.html) - Getting started with Python bindings
- [Python and C++ Integration (YouTube)](https://www.youtube.com/watch?v=_5T70cAXDJ0) - Practical pybind11 tutorial

### Core Computer Science Concepts

- [Immutable Objects](https://en.wikipedia.org/wiki/Immutable_object) - Understanding immutability in programming
- [Hash Functions](https://en.wikipedia.org/wiki/Hash_function) - Cryptographic and non-cryptographic hashing
- [Merkle Trees](https://en.wikipedia.org/wiki/Merkle_tree) - Tree structures for data integrity (used in Git)
- [Garbage Collection](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)) - Automatic memory
  management
- [Hash Functions Explained (YouTube)](https://www.youtube.com/watch?v=KqqOXndnvic) - MIT OpenCourseWare on hash
  functions
- [Immutable Data Structures (YouTube)](https://www.youtube.com/watch?v=Wo0qiGPSV-s) - Understanding immutability
  benefits

### Development Tools & Practices

- [Docker Getting Started](https://docs.docker.com/get-started/) - Containerization fundamentals
- [CMake Tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/) - Build system for C++ projects
- [pytest Documentation](https://docs.pytest.org/) - Python testing framework
- [Git Workflow](https://guides.github.com/introduction/flow/) - Collaborative development with Git
- [Docker Tutorial for Beginners (YouTube)](https://www.youtube.com/watch?v=3c-iBn73dDE) - TechWorld with Nana Docker
  course
- [CMake Tutorial (YouTube)](https://www.youtube.com/watch?v=nlKcXPUJGwA) - Complete CMake guide
- [pytest Tutorial (YouTube)](https://www.youtube.com/watch?v=etosV2IWBF0) - Python testing with pytest
- [Interactive Git Tutorial](https://learngitbranching.js.org/) - Visual and interactive Git learning

### Systems Programming

- [The Linux Programming Interface](http://man7.org/tlpi/) - Comprehensive systems programming guide
- [File Systems](https://en.wikipedia.org/wiki/File_system) - How data is stored and organized
- [Systems Programming Course](https://github.com/angrave/SystemProgramming/wiki) - University of Illinois systems
  programming wiki

### Advanced Topics

- [Idempotent Operations](https://en.wikipedia.org/wiki/Idempotence) - Operations that can be applied multiple times
  safely
- [RAII (Resource Acquisition Is Initialization)](https://en.cppreference.com/w/cpp/language/raii) - C++ resource
  management pattern
- [Python Memory Management](https://realpython.com/python-memory-management/) - How Python handles memory allocation
- [Memory Management in Python (YouTube)](https://www.youtube.com/watch?v=F6u5rhUQ6dU) - mCoding deep dive into Python
  memory
- [How Git Works Internally (YouTube)](https://www.youtube.com/watch?v=P6jD966jzlk) - ByteByteGo Git internals
  explanation
- [The Cherno C++ Series (YouTube)](https://www.youtube.com/playlist?list=PLlrATfBNZ98dudnM48yfGUldqGD0S4FFb) -
  Comprehensive modern C++ tutorial series
- [System Design Concepts (YouTube Channel)](https://www.youtube.com/@ByteByteGo) - ByteByteGo channel for systems
  concepts
- [Hussein Nasser (YouTube Channel)](https://www.youtube.com/@hnasr) - Database and systems programming concepts

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

While developed for educational purposes as part of the Advanced Systems Programming course, the code is available under
MIT License for learning and reference.

## 🐛 Issues and Support

If you encounter issues:

1. Check that Docker is running and up to date
2. Ensure all dependencies are properly installed
3. Run the test suite to identify specific problems
4. Consult the course staff for technical assistance

---

*Built with ❤️ for learning systems programming and version control internals*