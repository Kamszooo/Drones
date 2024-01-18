There are the following files:
•	generate_operators.py – the script  to generate operators (by default three). It outputs usernames (named User1, User2 etc.), salts, and hashed passwords to operators.json. Only the hashes and salts are stored, not the originally generated passwords (however they are printed to the console on generation).
•	operators.json – the .json file created by generate_operators.py. There is a default version inside the repository as per the requirement that “outputs of solution runs are meant to be in repository”. You need to run generate_operators.py on your own, since you need the original password to login (it will be printed to the console). 
•	main.py – the main file of the system. When it runs, the system operates and APIs works.
•	TRNG.py – the script for the True Random Number Generator, which uses BCryptGenRandom utility.
•	PRNG.py – the script for the Pseudo Random Number Generator. I uses the required implementation from Github.
•	templates/login.html – the .html template for the login window.

I explained much more details of how the system operates in my VLE Report.
