#include <iostream>
using namespace std;

bool isPrime(int n) {
    if (n <= 1)
    return false;
    for (int i = 2; i*i <= n; i++) 
    cout<<i;
    return 0;
}
int main() {
    int num;
    cout << "Enter a number: ";
    cin >> num;
    (isPrime(num))?cout << num << " is a prime number.\n":cout << num << " is not a prime number.\n";
    return 0;
}
