"""Plantilla del juego Arkanoid para el hito M2.

Completa los métodos marcados con TODO respetando las anotaciones de tipo y la
estructura de la clase. El objetivo es construir un prototipo jugable usando
pygame que cargue bloques desde un fichero de nivel basado en caracteres.
"""
from pathlib import Path

from arkanoid_core import *
# --------------------------------------------------------------------- #
# Métodos a completar por el alumnado
# --------------------------------------------------------------------- #

@arkanoid_method
def cargar_nivel(self) -> list[str]:
    """Lee el fichero de nivel y devuelve la cuadrícula como lista de filas."""
    if not self.level_path.is_file():
        raise FileNotFoundError(f"No encuentro el archivo en la ruta: {self.level_path}")

    lineas = [
        linea.strip()
        for linea in self.level_path.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]
    if not lineas:
        raise ValueError("El archivo de nivel está vacío.")

    ancho_primera_fila = len(lineas[0])
    for fila in lineas:
        if len(fila) != ancho_primera_fila:
            raise ValueError("Todas las filas del nivel deben tener el mismo ancho.")

    # - Guarda el resultado en `self.layout` y devuélvelo.
    self.layout = lineas
    return self.layout


@arkanoid_method
def preparar_entidades(self) -> None:
    """Posiciona paleta y bola, y reinicia puntuación y vidas."""
 
    # - Ajusta el tamaño de `self.paddle` y céntrala usando `midbottom`.   
    self.paddle.midbottom = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - self.PADDLE_OFFSET)

    # - Reinicia `self.score`, `self.lives` y `self.end_message`.
    self.score = 0
    self.lives = 3
    self.end_message = ""

    # - Llama a `self.reiniciar_bola()` para colocar la bola sobre la paleta.
    self.reiniciar_bola()

@arkanoid_method
def crear_bloques(self) -> None:
    """Genera los rectángulos de los bloques en base a la cuadrícula."""
    # - Limpia `self.blocks`, `self.block_colors` y `self.block_symbols`.
    self.blocks.clear()
    self.block_colors.clear()
    self.block_symbols.clear()
  
    # - Recorre `self.layout` para detectar símbolos de bloque.
    for fila_idx in range(len(self.layout)):
        fila = self.layout[fila_idx]
        for col_idx in range(len(fila)):
            simbolo = fila[col_idx]

            # - Usa `self.calcular_posicion_bloque` y rellena las listas paralelas.
            if simbolo in self.BLOCK_COLORS:
                rect = self.calcular_posicion_bloque(fila_idx, col_idx)
                self.blocks.append(rect)
                self.block_colors.append(self.BLOCK_COLORS[simbolo])
                self.block_symbols.append(simbolo)

@arkanoid_method
def procesar_input(self) -> None:
    """Gestiona la entrada de teclado para mover la paleta."""
    # - Obtén el estado de teclas con `self.obtener_estado_teclas()`.
    teclas = self.obtener_estado_teclas()
  
    # - Desplaza la paleta con `self.PADDLE_SPEED` si se pulsan las teclas izquierda/derecha.
    if teclas[self.KEY_LEFT] or teclas[self.KEY_A]:
        self.paddle.x -= self.PADDLE_SPEED
    if teclas[self.KEY_RIGHT] or teclas[self.KEY_D]:
        self.paddle.x += self.PADDLE_SPEED
     
    # - Limita la posición para que no salga de la pantalla.
    if self.paddle.left < 0:
        self.paddle.left = 0
    if self.paddle.right > self.SCREEN_WIDTH:
        self.paddle.right = self.SCREEN_WIDTH

@arkanoid_method
def actualizar_bola(self) -> None:
    """Actualiza la posición de la bola y resuelve colisiones."""
    if not self.running:
        return 
    
    # - Suma `self.ball_velocity` a `self.ball_pos` y genera `ball_rect` con `self.obtener_rect_bola()`.
    self.ball_pos += self.ball_velocity
    ball_rect = self.obtener_rect_bola()
    
    # - Gestiona rebotes con paredes, paleta y bloques, modificando velocidad y puntuación.
   #paredes 
    if ball_rect.left <= 0:
        self.ball_pos.x = self.BALL_RADIUS
        self.ball_velocity.x *= -1
    elif ball_rect.right >= self.SCREEN_WIDTH:
        self.ball_pos.x = self.SCREEN_WIDTH - self.BALL_RADIUS
        self.ball_velocity.x *= -1
     
     #techo   
    if ball_rect.top <= 0:
        self.ball_pos.y = self.BALL_RADIUS
        self.ball_velocity.y *= -1
        
    #paleta
    if ball_rect.colliderect(self.paddle) and self.ball_velocity.y > 0:
        self.ball_pos.y = self.paddle.top - self.BALL_RADIUS
        self.ball_velocity.y *= -1
    
    #bloques
    ball_rect = self.obtener_rect_bola()
    for i in range(len(self.blocks) - 1, -1, -1):
        bloque = self.blocks[i]
        if ball_rect.colliderect(bloque):
            simbolo = self.block_symbols[i]
            self.score += self.BLOCK_POINTS.get(simbolo, 50)
        
    # - Controla fin de nivel cuando no queden bloques y resta vidas si la bola cae.
            del self.blocks[i]
            del self.block_colors[i]
            del self.block_symbols[i]
            
            self.ball_velocity.y *= -1
            break

   # Condición de victoria (no quedan bloques)
    if len(self.blocks) == 0:
        self.running = False
        self.end_message = "¡VICTORIA! Pulsa ESC para salir"

    # Condición de derrota (la bola cae por debajo de la pantalla)
    if ball_rect.top >= self.SCREEN_HEIGHT:
        self.lives -= 1
        if self.lives > 0:
            self.reiniciar_bola()
        else:
            self.running = False
            self.end_message = "GAME OVER. Pulsa ESC para salir"



@arkanoid_method
def dibujar_escena(self) -> None:
    """Renderiza fondo, bloques, paleta, bola y HUD."""
    if not self.screen:
        return
    
    # - Rellena el fondo y dibuja cada bloque con `self.dibujar_rectangulo`.
    self.screen.fill(self.BACKGROUND_COLOR)
    
    for i in range(len(self.blocks)):
        self.dibujar_rectangulo(self.blocks[i], self.block_colors[i])
    
    # - Pinta la paleta y la bola con las utilidades proporcionadas.
    self.dibujar_rectangulo(self.paddle, self.PADDLE_COLOR)
    centro_bola = (int(self.ball_pos.x), int(self.ball_pos.y))
    self.dibujar_circulo(centro_bola, self.BALL_RADIUS, self.BALL_COLOR)
    
    
    # - Muestra puntuación, vidas y mensajes usando `self.dibujar_texto`.
    
    self.dibujar_texto(f"Puntuación: {self.score}", (20, 20))
    self.dibujar_texto(f"Vidas: {self.lives}", (self.SCREEN_WIDTH - 120, 20))
   
    if self.end_message:
        self.dibujar_texto(self.end_message, (self.SCREEN_WIDTH // 2 - 180, self.SCREEN_HEIGHT // 2), grande=True)

@arkanoid_method
def run(self) -> None:
    """Ejecuta el bucle principal del juego."""
    # - Inicializa recursos (`self.inicializar_pygame`, `self.cargar_nivel`, etc.).
    self.inicializar_pygame()
    try:
        self.cargar_nivel()
        self.preparar_entidades()
        self.crear_bloques()
        self.running = True

        # Bucle principal
        while self.clock is not None:
            for evento in self.iterar_eventos():
                if evento.type == self.EVENT_QUIT:
                    self.running = False
                    self.end_message = ""
                elif evento.type == self.EVENT_KEYDOWN:
                    if evento.key == self.KEY_ESCAPE:
                        self.running = False
                        self.end_message = ""

            if not self.running and not self.end_message:
                break

            if self.running:
                self.procesar_input()
                self.actualizar_bola()

            self.dibujar_escena()
            self.actualizar_pantalla()
            self.clock.tick(self.FPS)
    finally:
        self.finalizar_pygame()


def main() -> None:
    """Permite ejecutar el juego desde la línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Plantilla del hito M2: Arkanoid con pygame.",
    )
    parser.add_argument(
        "level",
        type=str,
        nargs="?",
        default=str(Path(__file__).resolve().parent / "niveles" / "demo.txt"),
        help="Ruta al fichero de nivel (por defecto: niveles/demo.txt).",
    )
    args = parser.parse_args()

    game = ArkanoidGame(args.level)
    game.run()


if __name__ == "__main__":
    main()