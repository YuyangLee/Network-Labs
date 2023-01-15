cmake_minimum_required(VERSION 3.22) # 觉得版本高了可自行调小，没问题
project(network_exp4_sdk)

set(CMAKE_CXX_STANDARD 17)

add_subdirectory(nlohmann_json)

add_executable(sdk src/main.cpp src/api.cpp src/api.h src/outgoing.cpp src/outgoing.h)

target_link_libraries(sdk PRIVATE nlohmann_json::nlohmann_json)