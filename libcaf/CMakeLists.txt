cmake_minimum_required(VERSION 3.28)
project(libcaf LANGUAGES CXX)

# Enable pybind11 from scikit-build-core
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 REQUIRED)

# Optionally enable coverage instrumentation
option(ENABLE_COVERAGE "Enable coverage instrumentation" OFF)
if(ENABLE_COVERAGE)
    message(STATUS "Building with coverage support")
endif()

add_library(_libcaf MODULE
    src/caf.cpp
    src/hash_types.cpp
    src/object_io.cpp
    src/bind.cpp
)

target_compile_features(_libcaf PRIVATE cxx_std_17)

# Warnings and treat warnings as errors
if (MSVC)
    target_compile_options(_libcaf PRIVATE /W4 /WX)
else()
    target_compile_options(_libcaf PRIVATE -Wall -Wextra -Werror)
endif()

# Coverage flags
if(ENABLE_COVERAGE)
    target_compile_options(_libcaf PRIVATE --coverage -fprofile-arcs -ftest-coverage -O0)
    target_link_options(_libcaf PRIVATE --coverage)
    target_link_libraries(_libcaf PRIVATE gcov)
endif()

target_link_libraries(_libcaf PRIVATE crypto pybind11::module)
target_include_directories(_libcaf PRIVATE ${pybind11_INCLUDE_DIRS})

pybind11_extension(_libcaf)

set_target_properties(_libcaf PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
