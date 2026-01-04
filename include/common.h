#ifndef COMMON_H
#define COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_QUESTIONS 100
#define MAX_STR_LEN 256
#define DATA_FILE "questions.txt"

// 题目结构体
typedef struct {
    int id;
    char content[MAX_STR_LEN];     // 题目
    char correct_answer[MAX_STR_LEN]; // 标准答案
    int score;                     // 分值
    
    // 以下字段用于考后分析
    char user_answer[MAX_STR_LEN]; // 用户填写的答案
    int obtained_score;            // 用户该题得分
} Question;

// --- 函数声明 ---

// get_data.c
int load_questions(const char* filename, Question* q_array);

// add_questions.c (新增)
void append_question_to_file(const char* filename);

// put_questions.c
void display_question(int index, Question q);
void display_wrong_questions(Question* q_array, int count); // 新增错题显示

// get_answer.c
void get_user_input(char* buffer, int size);

// grading.c
int calculate_score(const char* user_ans, const char* correct_ans, int full_score);

#endif