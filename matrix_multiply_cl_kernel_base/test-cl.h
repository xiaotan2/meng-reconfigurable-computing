#define MATRIX_RANK 50

#define A_SIZE 126
#define IA_SIZE 51
#define JA_SIZE 126
float A[126] = { 0.166667, 0.333333, 0.333333, 0.333333, 0.25, 0.2, 0.333333, 0.333333, 0.333333, 0.166667, 0.25, 0.25, 1, 0.166667, 0.5, 0.166667, 0.5, 0.5, 0.5, 0.25, 0.25, 1, 0.333333, 0.5, 0.25, 0.333333, 0.25, 0.333333, 0.333333, 0.5, 0.166667, 0.333333, 0.166667, 0.333333, 0.25, 0.5, 1, 0.25, 1, 0.2, 0.5, 0.5, 0.5, 0.333333, 0.5, 0.5, 0.333333, 0.333333, 0.5, 0.25, 0.333333, 0.333333, 0.333333, 0.5, 0.333333, 0.333333, 0.333333, 0.5, 0.333333, 0.5, 0.5, 0.333333, 0.333333, 0.333333, 0.333333, 0.25, 0.333333, 0.2, 0.5, 0.166667, 0.5, 0.166667, 0.25, 0.5, 0.166667, 0.333333, 0.5, 0.5, 0.333333, 1, 0.25, 0.5, 0.333333, 0.333333, 0.5, 0.5, 1, 0.333333, 0.25, 0.25, 0.5, 0.2, 0.25, 0.5, 0.166667, 0.5, 0.333333, 0.333333, 0.333333, 0.333333, 0.333333, 0.5, 0.5, 0.333333, 1, 0.166667, 0.2, 0.25, 1, 0.5, 1, 0.333333, 0.5, 0.333333, 0.333333, 0.25, 0.5, 0.5, 0.166667, 0.25, 0.5, 0.5, 0.333333, 0.5, 0.5, 0.25 };

int IA[51] = { 0, 1, 3, 4, 5, 7, 11, 14, 17, 20, 25, 25, 28, 29, 31, 35, 38, 39, 41, 43, 47, 48, 52, 59, 61, 64, 65, 67, 70, 74, 75, 78, 80, 82, 84, 88, 91, 93, 97, 100, 102, 104, 106, 110, 111, 113, 114, 117, 120, 123, 126 };

int JA[126] = { 10, 21, 49, 34, 20, 3, 24, 24, 27, 32, 37, 18, 22, 32, 0, 10, 44, 14, 33, 45, 12, 16, 26, 35, 37, 9, 12, 23, 48, 6, 32, 1, 10, 21, 45, 19, 40, 45, 46, 3, 4, 31, 39, 2, 8, 33, 34, 17, 11, 12, 23, 48, 1, 13, 21, 23, 28, 29, 49, 30, 47, 17, 27, 43, 2, 12, 26, 3, 4, 32, 6, 10, 18, 41, 10, 9, 11, 47, 27, 42, 18, 31, 2, 48, 0, 15, 25, 49, 20, 37, 38, 3, 20, 30, 32, 38, 43, 17, 24, 43, 28, 44, 19, 34, 7, 10, 3, 18, 36, 39, 5, 28, 41, 1, 9, 20, 35, 13, 32, 37, 8, 14, 26, 15, 29, 45 };
