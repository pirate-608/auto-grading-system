#include "common.h"

void append_question_to_file(const char* filename) {
    FILE* file = fopen(filename, "a"); // 以追加模式打开
    if (!file) {
        printf("无法打开文件进行写入。\n");
        return;
    }

    char content[MAX_STR_LEN];
    char answer[MAX_STR_LEN];
    char score_str[20];

    printf("\n=== 添加新题目 (输入 'exit' 取消) ===\n");

    // 1. 输入题目内容
    printf("请输入题目描述 (不要包含 '|' 符号): ");
    get_user_input(content, MAX_STR_LEN);
    if (strcmp(content, "exit") == 0) { fclose(file); return; }

    // 2. 输入答案
    printf("请输入标准答案: ");
    get_user_input(answer, MAX_STR_LEN);

    // 3. 输入分值
    printf("请输入分值 (整数): ");
    get_user_input(score_str, 20);
    int score = atoi(score_str);
    if (score <= 0) score = 10; // 默认分值

    // 写入文件，格式: 题目|答案|分值
    fprintf(file, "\n%s|%s|%d", content, answer, score);

    printf("-> 题目已成功保存到题库！\n");
    fclose(file);
}