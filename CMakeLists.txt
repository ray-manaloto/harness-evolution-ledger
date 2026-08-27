cmake_minimum_required(VERSION 4.4.3)

project(
  harness_evolution_ledger
  VERSION 0.0.0
  DESCRIPTION
    "Local-first Claude and Codex telemetry replay and improvement engine"
  LANGUAGES CXX)

include(CTest)

add_executable(hel_phase0_smoke tests/phase0_smoke.cpp)
target_compile_features(hel_phase0_smoke PRIVATE cxx_std_26)
set_target_properties(
  hel_phase0_smoke
  PROPERTIES CXX_EXTENSIONS OFF
             CXX_SCAN_FOR_MODULES OFF
             CXX_STANDARD_REQUIRED ON)

if(MSVC)
  target_compile_options(hel_phase0_smoke PRIVATE /W4 /WX)
else()
  target_compile_options(hel_phase0_smoke PRIVATE -Wall -Wextra -Wpedantic
                                                  -Werror)
endif()

add_test(NAME phase0.smoke COMMAND hel_phase0_smoke)

option(HEL_P2996_CONTROL "Build the devcontainer-only P2996 reflection control"
       OFF)
if(HEL_P2996_CONTROL)
  add_executable(hel_p2996_control tests/p2996_smoke.cpp)
  target_compile_features(hel_p2996_control PRIVATE cxx_std_26)
  target_compile_options(hel_p2996_control PRIVATE -freflection-latest -Wall
                                                   -Wextra -Werror)
  set_target_properties(
    hel_p2996_control
    PROPERTIES CXX_EXTENSIONS OFF
               CXX_SCAN_FOR_MODULES OFF
               CXX_STANDARD_REQUIRED ON)
  add_test(NAME phase0.p2996-reflection COMMAND hel_p2996_control)
endif()
