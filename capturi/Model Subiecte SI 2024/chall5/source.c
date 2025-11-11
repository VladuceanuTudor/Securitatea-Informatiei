#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<time.h>


int global_cookie = 0;
char binsh[] = "/bin/sh"; 


void do_nothing(){

	system("/bin/ls");

}

void check_stack(int cookie){

	if(cookie != global_cookie){
		puts("You don't own the right cookie");
		exit(-1);
	}

}


int main(){
	srand(time(0));

	int cookie = rand();
	global_cookie = cookie;

	char buffer[64];
	puts("Hello from main function!\nGive me a message:");
	fgets(buffer,256,stdin);
	
	check_stack(cookie);
	

	return 0;
}
