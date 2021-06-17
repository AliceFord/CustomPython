#include <bits/stdc++.h>

int main() {
int n = 100;
std::vector<bool> a = {};
int i = 0;
while (i<n) {
a.push_back(true);
i++;
};
i = 2;
while (i<ceil(sqrt(n))) {
if (a[i]) {
int j = pow(i,2);
while (j<n) {
a[j]=false;
j+=i;
};
};
i++;
};
i = 2;
while (i<a.size()) {
if (a[i]) {
std::cout << (i) << ("\n");
};
i++;
};

}