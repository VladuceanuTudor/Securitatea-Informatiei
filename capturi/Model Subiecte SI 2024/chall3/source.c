#include<stdio.h>
#include<stdlib.h>
#include<string.h>







int main(){


	char buffer[64];
	printf("Enjoy your leak %.04x\n",buffer+32);
	puts("Hello from main function!\nGive me a message:");
	fgets(buffer,128,stdin);

	return 0;
}
