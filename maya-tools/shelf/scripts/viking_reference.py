import reference
from byugui import message_gui
from byuam import Environment

def go():
	result = message_gui.yes_or_no('This is only for Vikings. Are you sure you want to continue?')
	if result:
		reference.go(useNamespace=True)
	env = Environment()
	user = env.get_current_username()
	if user == 'carlilet':
		message_gui.info('Hey Thad, I made this for you!')
