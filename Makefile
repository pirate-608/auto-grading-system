CC = gcc
CFLAGS = -Wall -g -Iinclude
OBJ = main.o get_data.o put_questions.o get_answer.o grading.o add_questions.o
BUILD_DIR = build
TARGET = $(BUILD_DIR)/auto_grader.exe
LIB_TARGET = $(BUILD_DIR)/libgrading.dll

all: $(TARGET) $(LIB_TARGET)

$(TARGET): $(OBJ) | $(BUILD_DIR)
	$(CC) $(OBJ) -o $(TARGET)

$(LIB_TARGET): src/grading.c include/common.h | $(BUILD_DIR)
	$(CC) -shared -o $(LIB_TARGET) src/grading.c -Iinclude

$(BUILD_DIR):
	if not exist $(BUILD_DIR) mkdir $(BUILD_DIR)

%.o: src/%.c include/common.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	del *.o
	if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR)

clean:
	del /Q $(OBJ)
	if exist $(BUILD_DIR) rmdir /S /Q $(BUILD_DIR)