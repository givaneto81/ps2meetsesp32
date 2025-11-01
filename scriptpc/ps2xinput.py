import serial
import vgamepad as vg
import time
import sys

# --- Configuração ---
# ! AJUSTE AQUI a porta COM em que o ESP32 apareceu (ex: "COM3", "COM5", etc.)
PORTA_SERIAL = "COM3"
BAUD_RATE = 115200
# --------------------

# Mapeamento dos botões PS2 (índice da PS2X_lib) para botões XInput (vgamepad)
# PS2X_lib Index -> vgamepad Button Constant
ps2_to_xinput_map = {
    0: vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,       # SELECT
    1: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,  # L3 (Click analógico esquerdo)
    2: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB, # R3 (Click analógico direito)
    3: vg.XUSB_BUTTON.XUSB_GAMEPAD_START,       # START
    4. vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,     # DPAD UP
    5: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,  # DPAD RIGHT
    6: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,   # DPAD DOWN
    7: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,   # DPAD LEFT
    8: None, # L2 (Botão digital, ignorado pois usamos o analógico)
    9: None, # R2 (Botão digital, ignorado pois usamos o analógico)
    10: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, # L1
    11: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER, # R1
    12: vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,         # Triangle (Y)
    13: vg.XUSB_BUTTON.XUSB_GAMEPAD_B,         # Circle (B)
    14: vg.XUSB_BUTTON.XUSB_GAMEPAD_A,         # Cross (A)
    15: vg.XUSB_BUTTON.XUSB_GAMEPAD_X          # Square (X)
}


def map_axis_stick(v):
    """Mapeia 0-255 (centro 128) para -32768 a 32767."""
    return int((v - 128) * 256.0)


def map_axis_trigger(v):
    """Mapeia 0-255 (pressão PS2) para 0-255 (gatilho XInput)."""
    return int(v)


def main():
    try:
        print("Iniciando gamepad virtual (XInput)...")
        gamepad = vg.VX360Gamepad()
        print("Gamepad virtual criado com sucesso.")
    except Exception as e:
        print(f"Erro fatal: Falha ao iniciar o ViGEmBus.")
        print(f"Verifique se o driver ViGEmBus está instalado.")
        print(f"Detalhe: {e}")
        input("Pressione Enter para sair...")
        sys.exit(1)

    ser = None
    while True:
        try:
            if ser is None:
                print(f"Tentando conectar à porta serial {PORTA_SERIAL} a {BAUD_RATE} bps...")
                ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
                print("Conectado. Aguardando dados do ESP32...")

            line = ser.readline().decode('utf-8', errors='ignore').strip()

            # Formato esperado: "AX lx ly rx ry l2 r2 BTN b0 b1 ... b15"
            if not line.startswith("AX"):
                continue

            parts = line.split()

            # Validação do pacote de dados (1+6 eixos + 1+16 botões = 24 partes)
            if len(parts) != 24 or parts[7] != "BTN":
                print(f"Dado malformado recebido, descartando: {line}")
                continue

            # --- Processamento dos Eixos ---
            # O eixo Y do PS2 é invertido (0=cima, 255=baixo)
            # O XInput espera positivo para cima. Invertemos multiplicando por -1.

            lx = map_axis_stick(int(parts[1]))
            ly = map_axis_stick(int(parts[2])) * -1  # Inverte Eixo Y
            rx = map_axis_stick(int(parts[3]))
            ry = map_axis_stick(int(parts[4])) * -1  # Inverte Eixo Y

            l2_trigger = map_axis_trigger(int(parts[5]))
            r2_trigger = map_axis_trigger(int(parts[6]))

            gamepad.left_joystick(x_value=lx, y_value=ly)
            gamepad.right_joystick(x_value=rx, y_value=ry)
            gamepad.left_trigger(value=l2_trigger)
            gamepad.right_trigger(value=r2_trigger)

            # --- Processamento dos Botões ---
            # Pega a lista dos 16 estados de botões (partes 8 a 23)
            button_states = parts[8:]

            for i in range(16):
                state = (button_states[i] == "1")  # True se "1", False se "0"
                target_button = ps2_to_xinput_map.get(i)

                # Se o botão existe no mapeamento (não é None)
                if target_button is not None:
                    if state:
                        gamepad.press_button(button=target_button)
                    else:
                        gamepad.release_button(button=target_button)

            # Envia o estado atualizado para o driver ViGEmBus
            gamepad.update()

            # Pequeno sleep para não sobrecarregar o loop Python
            time.sleep(0.005)  # ~5ms

        except serial.SerialException as se:
            print(f"Erro serial: {se}. Tentando reconectar em 5s...")
            if ser:
                ser.close()
            ser = None
            time.sleep(5)
        except Exception as e:
            print(f"Erro inesperado no loop: {e}")
            print(f"Linha problemática: {line}")
            time.sleep(1)


if __name__ == "__main__":
    main()