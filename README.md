# PS2MEETSESP32

Este projeto transforma um controle de PlayStation 2 (DualShock 2) em um controle XInput (Xbox 360) virtual para PC, utilizando um ESP32.

A comunicação é feita via Serial (USB) e um script Python que mapeia os dados seriais para um gamepad virtual usando ViGEmBus. O resultado é um controle de baixa latência, reconhecido nativamente pela maioria dos jogos modernos e emuladores.

## Funcionalidades

* **XInput Nativo:** Reconhecido pelo Windows como um "Xbox 360 Controller".
* **Analógicos Completos:** Suporte para sticks Esquerdo (LX, LY) e Direito (RX, RY).
* **Gatilhos Analógicos:** L2 e R2 funcionam como gatilhos analógicos (0-255), usando o sensor de pressão do DualShock 2.
* **Mapeamento Completo:** Todos os botões (D-Pad, A/B/X/Y, Start/Select, L1/R1, L3/R3) são mapeados.
* **Baixa Latência:** A comunicação serial a 115200 bps garante uma resposta rápida.
* **"Headless":** Nenhum software visual é necessário, apenas um script Python rodando em segundo plano.

## 1. Hardware Necessário

* 1x ESP32-WROOM-32 (ou qualquer variante ESP32 com pinos suficientes)
* 1x Controle de PlayStation 2 (original ou clone)
* Fios para conexão

## 2. Conexões Elétricas (Fiação)

**ATENÇÃO:** O ESP32 opera em 3.3V. **Sempre** conecte o VCC do controle ao pino `3.3V` do ESP32, NUNCA ao `5V` (VIN), para evitar danos.

O fio de Rumble (7.5V-9V) do controle **não deve ser conectado** por segurança.

### Mapeamento (Seu Controle Clone)

| Sinal (Controle) | Cor (Seu Controle) | ESP32 Pin |
| :--- | :--- | :--- |
| **vcc** | Vermelho | `3V3` |
| **gnd** | Preto | `GND` |
| **do** (Data Out) | Branco | `GPIO 19` |
| **di** (Data In) | Marrom | `GPIO 23` |
| **cs** (Chip Select)| Amarelo | `GPIO 5` |
| **clk** | Azul | `GPIO 18` |
| **ack** | Verde | *(NÃO CONECTAR)* |
| **7,5v** (Rumble) | Roxo | **(PERIGO - NÃO CONECTAR)** |

### Mapeamento (Controle Original Padrão)

| Sinal PS2 | Cor (Padrão) | ESP32 Pin |
| :--- | :--- | :--- |
| **VCC** | Marrom | `3V3` |
| **GND** | Preto | `GND` |
| **DATA** | Verde | `GPIO 19` |
| **CMD** | Laranja | `GPIO 23` |
| **ATT** | Azul | `GPIO 5` |
| **CLK** | Amarelo | `GPIO 18` |

## 3. Dependências de Software (PC)

Antes de rodar o script, seu PC precisa dos seguintes softwares:

1.  **Python 3.10+:** [python.org](https://www.python.org/downloads/) (Marque "Add Python to PATH" durante a instalação).
2.  **Driver ViGEmBus:** Necessário para criar o gamepad virtual.
    * [Baixe o instalador na página oficial de releases](https://github.com/ViGEm/ViGEmBus/releases).
3.  **Bibliotecas Python:** Abra um CMD/PowerShell e instale:
    ```shell
    pip install pyserial vgamepad
    ```

## 4. Como Usar

### Parte 1: Firmware (ESP32)

1.  Clone este repositório.
2.  Baixe a biblioteca `PS2X_lib` [neste link](https://github.com/madsci/Arduino-PS2X/archive/refs/heads/master.zip).
3.  Descompacte o arquivo. Renomeie a pasta para `Arduino-PS2X-master` (se necessário) e coloque-a dentro da pasta `lib/` do projeto.
4.  Abra o projeto no Visual Studio Code com a extensão PlatformIO.
5.  Conecte o ESP32 ao PC.
6.  Clique no ícone de Seta (Upload) na barra de status azul do PlatformIO (canto inferior esquerdo) para compilar e carregar o firmware.

### Parte 2: Script (PC)

1.  Conecte o ESP32 (com o firmware carregado) ao PC.
2.  Abra o Gerenciador de Dispositivos do Windows e vá em "Portas (COM & LPT)" para descobrir qual porta COM o ESP32 está usando (ex: `COM3`).
3.  Edite o arquivo `pc_script/run_ps2_to_xinput.py` e atualize a variável `PORTA_SERIAL` com o número da sua porta COM.
4.  Abra um terminal, navegue até a pasta do projeto e execute o script:
    ```shell
    python pc_script/run_ps2_to_xinput.py
    ```
5.  Se tudo estiver correto, você verá a mensagem "Gamepad virtual criado com sucesso."

## 5. Validação

1.  Com o script Python rodando, pressione o botão "Windows".
2.  Digite `joy.cpl` e pressione Enter.
3.  O "Controller (Xbox 360 for Windows)" deve aparecer na lista.
4.  Selecione-o e clique em `Propriedades`.
5.  Teste todos os eixos, botões e gatilhos na tela de teste.

## Melhorias Futuras

* [ ] **Implementar Rumble (Vibração):** Exigirá um circuito de acionamento externo (Transistor MOSFET) para alimentar com segurança o motor de 7.5V do controle, além de software bidirecional para receber comandos de "rumble" do ViGEmBus.
* [ ] **Auto-detecção da Porta COM:** O script Python pode ser melhorado para tentar encontrar o ESP32 automaticamente, em vez de exigir a configuração manual da `PORTA_SERIAL`.