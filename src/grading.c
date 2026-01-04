#include "common.h"
#include <ctype.h>

// 内部辅助：转小写
void to_lower_string(char* dest, const char* src) {
    while (*src) {
        *dest = tolower((unsigned char)*src);
        dest++;
        src++;
    }
    *dest = '\0';
}

int calculate_score(const char* user_ans, const char* correct_ans, int full_score) {
    char u_lower[MAX_STR_LEN];
    char c_lower[MAX_STR_LEN];

    to_lower_string(u_lower, user_ans);
    to_lower_string(c_lower, correct_ans);

    if (strcmp(u_lower, c_lower) == 0) {
        return full_score;
    }
    return 0;
}