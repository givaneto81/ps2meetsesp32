#include <Arduino.h>
#include <PS2X_lib.h> 

PS2X ps2x;

// Mapeamento de Pinos (Conforme ETAPA 2)
#define PS2_CLK 18 // Fio Azul (Seu controle)
#define PS2_CMD 23 // Fio Marrom (DI)
#define PS2_ATT 5  // Fio Amarelo (CS)
#define PS2_DAT 19 // Fio Branco (DO)

int error = 0;

void setup() {
  Serial.begin(115200);

  // (CLK, CMD, ATT, DATA, Pressures, Rumble)
  // Habilitamos "Pressures" (true) para ler os gatilhos L2/R2
  // Desabilitamos "Rumble" (false) por enquanto
  error = ps2x.config_gamepad(PS2_CLK, PS2_CMD, PS2_ATT, PS2_DAT, true, false);

  if (error == 0) {
    Serial.println("Controle PS2 Encontrado. Pressão analógica ATIVADA.");
  } else {
    Serial.println("Erro na inicialização do Controle PS2.");
  }
}

void loop() {
  // Se o controle não foi encontrado, não faz nada.
  if (error != 0) {
    delay(500);
    return;
  }

  // Ler o estado do controle
  ps2x.read_gamepad(false, 0); // (false = não requer nova leitura, 0 = sem vibração)

  // 1. Eixos dos Analógicos (0-255, centro ~128)
  int lx = ps2x.Analog(PSS_LX);
  int ly = ps2x.Analog(PSS_LY);
  int rx = ps2x.Analog(PSS_RX);
  int ry = ps2x.Analog(PSS_RY);

  // 2. Eixos dos Gatilhos (Pressão 0-255)
  int l2 = ps2x.Analog(PSAB_L2);
  int r2 = ps2x.Analog(PSAB_R2);

  // 3. Montar a string serial
  // Formato: "AX [eixos] BTN [botões]"

  Serial.print("AX"); // Identificador de Eixos
  Serial.print(" "); Serial.print(lx);
  Serial.print(" "); Serial.print(ly);
  Serial.print(" "); Serial.print(rx);
  Serial.print(" "); Serial.print(ry);
  Serial.print(" "); Serial.print(l2);
  Serial.print(" "); Serial.print(r2);

  Serial.print(" BTN"); // Identificador de Botões

  // 4. Botões Digitais (0-15)
  // Envia o estado (0 ou 1) de todos os 16 botões
  for (int i = 0; i < 16; i++) {
    Serial.print(" ");
    // ps2x.Button(i) retorna 1 se o botão 'i' estiver pressionado
    Serial.print(ps2x.Button(i));
  }

  Serial.println(); // Fim do pacote de dados

  delay(10); // Taxa de atualização de ~100Hz
}