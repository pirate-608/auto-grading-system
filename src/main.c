#include "common.h"
#include <time.h>
#ifdef _WIN32
#include <windows.h>
#endif

void clear_screen() {
    #ifdef _WIN32
        system("cls");
    #else
        system("clear");
    #endif
}

void shuffle_questions(Question *array, int n) {
    if (n > 1) {
        for (int i = n - 1; i > 0; i--) {
            int j = rand() % (i + 1);
            Question t = array[i];
            array[i] = array[j];
            array[j] = t;
        }
    }
}

void start_exam() {
    clear_screen();
    Question questions[MAX_QUESTIONS];
    int count = load_questions(DATA_FILE, questions);

    if (count == 0) {
        printf(ANSI_COLOR_RED "题库为空，请先在主菜单添加题目！\n" ANSI_COLOR_RESET);
        printf("按回车键返回...");
        getchar();
        return;
    }

    // 随机打乱题目顺序
    shuffle_questions(questions, count);

    int total_score = 0;
    int max_score = 0;

    printf(ANSI_COLOR_CYAN "\n>>> 考试开始 (共 %d 题) <<<\n" ANSI_COLOR_RESET, count);

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
    clear_screen();
    printf(ANSI_COLOR_MAGENTA "\n################ 成绩单 ################\n" ANSI_COLOR_RESET);
    printf("最终得分: " ANSI_BOLD "%d" ANSI_COLOR_RESET " / %d\n", total_score, max_score);
    
    // 5. 显示错题
    display_wrong_questions(questions, count);
    
    printf("\n按回车键返回主菜单...");
    getchar(); 
}

int main() {
#ifdef _WIN32
    SetConsoleOutputCP(65001); // Set console output to UTF-8
#endif
    srand(time(NULL)); // 初始化随机数种子

    char choice_str[10];
    int choice = 0;

    while (1) {
        clear_screen();
        // 主菜单界面
        printf(ANSI_COLOR_CYAN "\n======= C语言自动评分系统 =======\n" ANSI_COLOR_RESET);
        printf(ANSI_COLOR_GREEN "1." ANSI_COLOR_RESET " 开始考试\n");
        printf(ANSI_COLOR_GREEN "2." ANSI_COLOR_RESET " 添加题目到题库\n");
        printf(ANSI_COLOR_GREEN "3." ANSI_COLOR_RESET " 退出系统\n");
        printf(ANSI_COLOR_CYAN "=================================\n" ANSI_COLOR_RESET);
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
                printf(ANSI_COLOR_YELLOW "感谢使用，再见！\n" ANSI_COLOR_RESET);
                return 0;
            default:
                printf(ANSI_COLOR_RED "输入无效，请重新选择。\n" ANSI_COLOR_RESET);
                printf("按回车键继续...");
                getchar();
        }
    }
}