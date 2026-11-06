// Вкладені області видимості, цикл, розгалуження, коротке замикання.
int main() {
    int i = 1;
    int sum = 0;
    while (i <= 5) {
        int square = i * i;
        if (i % 2 != 0) sum = sum + square;
        i = i + 1;
    }
    {
        int sum = -7 / 3;
        printf("%d\n", sum);
    }
    if (sum == 35 || 1 / 0) printf("%d\n", sum);
    return sum;
}