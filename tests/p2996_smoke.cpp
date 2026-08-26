#include <meta>

constexpr std::meta::info reflected = ^^int;
static_assert(std::meta::is_type(reflected));

int main() {}
