#include "common.h"

void display_question(int index, Question q) {
    printf("\n----------------------------------------\n");
    printf("[第 %d 题] (%d 分)\n", index + 1, q.score);
    printf("题目: %s\n", q.content);
    printf("请输入答案: ");
}

void display_wrong_questions(Question* q_array, int count) {
    printf("\n================ 错题回顾 ================\n");
    int wrong_count = 0;

    for (int i = 0; i < count; i++) {
        // 如果得分小于满分，视为有错误（或未完全正确）
        if (q_array[i].obtained_score < q_array[i].score) {
            wrong_count++;
            printf("----------------------------------------\n");
            printf("题目 %d: %s\n", q_array[i].id, q_array[i].content);
            printf("  [-] 你的回答: %s\n", 
                   (strlen(q_array[i].user_answer) > 0) ? q_array[i].user_answer : "(未作答)");
            printf("  [+] 正确答案: %s\n", q_array[i].correct_answer);
        }
    }

    if (wrong_count == 0) {
        printf("恭喜！没有错题，全对！\n");
    } else {
        printf("\n共发现 %d 道错题，请复习。\n", wrong_count);
    }
    printf("==========================================\n");
}