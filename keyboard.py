from datetime import datetime
import threading

from commands import *
import buffer
import state
import gui
from communication import send_message

def watch_keys():
    while True:
        try:
            p_key_pressed = gui.stdscr.get_wch()
            key_pressed = ord(p_key_pressed)

            if key_pressed == 10: # Enter
                # Verifica se o que está no buffer se trata de um comando
                # Se for, o processa
                # Do contrário, assume-se ser uma mensagem
                if  buffer.get_buffer().startswith("!"):
                    process_command(buffer.get_buffer())
                else:
                    send_message(buffer.get_buffer())
                # E então limpa o buffer
                buffer.clear_buffer()
            elif key_pressed == 127: # Backspace
                buffer.backspace()
            elif (32 <= key_pressed <= 126 or 192 <= key_pressed <= 255): # Caractere normal
                buffer.append(chr(key_pressed))
            elif key_pressed == 27:
                # Tecla especial (como setas)

                # Lê as próximas duas para determinar qual foi a tecla pressionada
                cod_0 = ord(gui.stdscr.get_wch())
                cod_1 = ord(gui.stdscr.get_wch())

                if cod_0 == 91:
                    # Setas
                    if cod_1 == 65: # Cima
                        pass
                    elif cod_1 == 66:
                        pass
                    elif cod_1 == 67:
                        pass
                    elif cod_1 == 68:
                        pass
                
        except Exception:
            pass


def start_keyboard_listening():
    y = threading.Thread(target=watch_keys)
    y.name = "Keyboard-THREAD"
    y.start()