#This project is a project

def intro():
    name = input('What is your name?  ')
    age = input('What is your age?  ')
    gender = input('What is your gender?  ')

    print(f'Hello {name}, you are a {age} year old {gender}! Got it. ')
    print(f'It is fun getting to know you {name}!')
    print('Tell me some more about yourself: ')

    food = input('Can you tell me what your favorite food is?  ')
    color = input('What is your favorite color?  ')

    print(f' Alright {name}, lets make sure I have this straight. You are {age} and love {food} with {color} as your favorite color, right?  ')
intro()
answer = input('Y or N:  ')
if input == 'N':
    intro()
else:
    print('ok bye')