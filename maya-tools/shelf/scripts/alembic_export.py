import alembic_exporter
import alembic_static_exporter
from byugui import message_gui

def go():
	result = message_gui.binary_option("Would you like to export the animated or the static geo?", "Animated", "Static")
	if result is None:
		return;
	if result:
		alembic_exporter.go()
	else:
		alembic_static_exporter.go()
