#include<stdio.h>
#include<stdlib.h>
#include<string.h>


int do_something(){

	return system("/bin/ls");

}

int do_something_little(){

	return system("pwd");

}

int do_something_interesting(){


	return system("/bin/sh");
}



int do_nothing_function(){

	return 0;
}


int main(){


	char buffer[64];
	puts("Hello from main function!\nGive me a message:");
	fgets(buffer,128,stdin);

	return 0;
}
