#include "common.h"
#include <ctype.h>

#define MIN(a,b) (((a)<(b))?(a):(b))
#define MIN3(a,b,c) MIN(MIN(a,b),c)

// 内部辅助：转小写
void to_lower_string(char* dest, const char* src) {
    while (*src) {
        *dest = tolower((unsigned char)*src);
        dest++;
        src++;
    }
    *dest = '\0';
}

// Levenshtein Distance (编辑距离) 算法
int levenshtein_distance(const char *s1, const char *s2) {
    int len1 = strlen(s1);
    int len2 = strlen(s2);
    
    // 使用静态缓冲区避免频繁 malloc，假设最大长度 MAX_STR_LEN
    // 注意：如果 MAX_STR_LEN 很大，应考虑动态分配
    int matrix[MAX_STR_LEN + 1][MAX_STR_LEN + 1];

    for (int i = 0; i <= len1; i++) {
        matrix[i][0] = i;
    }
    for (int j = 0; j <= len2; j++) {
        matrix[0][j] = j;
    }

    for (int i = 1; i <= len1; i++) {
        for (int j = 1; j <= len2; j++) {
            int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            matrix[i][j] = MIN3(
                matrix[i - 1][j] + 1,       // deletion
                matrix[i][j - 1] + 1,       // insertion
                matrix[i - 1][j - 1] + cost // substitution
            );
        }
    }

    return matrix[len1][len2];
}

int calculate_score(const char* user_ans, const char* correct_ans, int full_score) {
    char u_lower[MAX_STR_LEN];
    char c_lower[MAX_STR_LEN];

    // 1. 预处理：转小写
    to_lower_string(u_lower, user_ans);
    to_lower_string(c_lower, correct_ans);

    // 2. 移除首尾空格 (简单处理，这里假设输入已经比较干净，或者在 Python 端处理过)
    // C 语言处理 trim 比较麻烦，这里暂时依赖 Python 端的 strip()

    // 3. 精确匹配
    if (strcmp(u_lower, c_lower) == 0) {
        return full_score;
    }

    // 4. 模糊匹配 (Fuzzy Matching)
    int len = strlen(c_lower);
    int dist = levenshtein_distance(u_lower, c_lower);

    // 容错规则：
    // - 长度 <= 3: 必须完全匹配 (dist == 0)
    // - 长度 4-6: 允许 1 个错误
    // - 长度 > 6: 允许 2 个错误
    int allowed_errors = 0;
    if (len > 6) {
        allowed_errors = 2;
    } else if (len >= 4) {
        allowed_errors = 1;
    }

    if (dist <= allowed_errors) {
        return full_score;
    }

    return 0;
}