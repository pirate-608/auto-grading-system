#include "common.h"

int load_questions(const char* filename, Question* q_array) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        // 如果文件不存在，创建一个空的
        file = fopen(filename, "w");
        if(file) fclose(file);
        return 0;
    }

    char line[MAX_STR_LEN * 3];
    int count = 0;

    while (fgets(line, sizeof(line), file) && count < MAX_QUESTIONS) {
        // 跳过空行
        if (strlen(line) < 2) continue;

        line[strcspn(line, "\n")] = 0;

        char* token = strtok(line, "|");
        if (!token) continue;
        
        q_array[count].id = count + 1;
        strcpy(q_array[count].content, token);

        token = strtok(NULL, "|");
        if (!token) continue;
        strcpy(q_array[count].correct_answer, token);

        token = strtok(NULL, "|");
        if (!token) continue;
        q_array[count].score = atoi(token);

        // 初始化考试状态字段
        q_array[count].obtained_score = 0;
        memset(q_array[count].user_answer, 0, MAX_STR_LEN);

        count++;
    }

    fclose(file);
    return count;
}