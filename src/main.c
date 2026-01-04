#include "common.h"
#ifdef _WIN32
#include <windows.h>
#endif

void start_exam() {
    Question questions[MAX_QUESTIONS];
    int count = load_questions(DATA_FILE, questions);

    if (count == 0) {
        printf("题库为空，请先在主菜单添加题目！\n");
        return;
    }

    int total_score = 0;
    int max_score = 0;

    printf("\n>>> 考试开始 (共 %d 题) <<<\n", count);

    for (int i = 0; i < count; i++) {
        // 1. 显示题目
        display_question(i, questions[i]);

        // 2. 获取用户输入
        get_user_input(questions[i].user_answer, MAX_STR_LEN);

        // 3. 判分并保存结果
        questions[i].obtained_score = calculate_score(
            questions[i].user_answer, 
            questions[i].correct_answer, 
            questions[i].score
        );

        // 累计分数
        total_score += questions[i].obtained_score;
        max_score += questions[i].score;
    }

    // 4. 考试结束报告
    printf("\n################ 成绩单 ################\n");
    printf("最终得分: %d / %d\n", total_score, max_score);
    
    // 5. 显示错题
    display_wrong_questions(questions, count);
    
    printf("\n按回车键返回主菜单...");
    getchar(); 
}

int main() {
#ifdef _WIN32
    SetConsoleOutputCP(65001); // Set console output to UTF-8
#endif
    char choice_str[10];
    int choice = 0;

    while (1) {
        // 主菜单界面
        printf("\n======= C语言自动评分系统 =======\n");
        printf("1. 开始考试\n");
        printf("2. 添加题目到题库\n");
        printf("3. 退出系统\n");
        printf("=================================\n");
        printf("请选择操作 (1-3): ");

        get_user_input(choice_str, sizeof(choice_str));
        choice = atoi(choice_str);

        switch (choice) {
            case 1:
                start_exam();
                break;
            case 2:
                append_question_to_file(DATA_FILE);
                break;
            case 3:
                printf("感谢使用，再见！\n");
                return 0;
            default:
                printf("输入无效，请重新选择。\n");
        }
    }
}